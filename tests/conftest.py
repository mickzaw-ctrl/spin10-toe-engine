"""
Shared pytest configuration.

Two things happen here:

1. ``src`` is put on ``sys.path`` so the suite runs with a bare
   ``python -m pytest tests`` - ``PYTHONPATH=src`` is no longer required.

2. A ``tr`` fixture is provided.  ``test_grand_unified_toe.py``,
   ``test_quantum_gravity.py``, ``test_teleportation.py`` and
   ``test_teleportation_deep.py`` are written as standalone scripts whose test
   functions take a results-accumulator parameter (``TestResults`` in the first
   two, ``TR`` in the latter two).  Without this fixture pytest cannot even
   collect them and reports 33 setup errors while running nothing.  The fixture
   instantiates the accumulator defined by the requesting module and asserts at
   teardown that no internal check failed, so those ~224 checks now count
   towards the pytest result instead of only towards the script's own exit code.
"""

import os
import sys

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


@pytest.fixture
def tr(request):
    module = request.module
    accumulator = getattr(module, 'TestResults', None) or getattr(module, 'TR', None)
    if accumulator is None:
        pytest.skip('{} defines no TestResults/TR accumulator'.format(module.__name__))

    results = accumulator()
    yield results

    # The accumulators are not uniform: TestResults counts `.failed`, TR counts `.f`.
    failed = getattr(results, 'failed', None)
    if failed is None:
        failed = getattr(results, 'f', None)
    if failed is None:
        return
    passed = getattr(results, 'passed', None)
    if passed is None:
        passed = getattr(results, 'p', 0)
    assert failed == 0, '{}: {}/{} internal checks failed'.format(
        request.node.name, failed, failed + passed)
