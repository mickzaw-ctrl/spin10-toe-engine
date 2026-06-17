"""
Benchmark v3 – poprawiony pomiar czasu (zewnętrzny dla obu klas).
RAW: różne seed per iteracja. CACHE: ten sam seed.
"""

import time
import jax
import jax.numpy as jnp
from jax import vmap, jit

print(f"Device: {jax.devices()[0].platform} | JAX: {jax.__version__}")

# -----------------------------------------------------------------------------
# Baseline
# -----------------------------------------------------------------------------
class Spin10Baseline:
    def __init__(self, bond_dimension=10):
        self.bond_dim = bond_dimension
    @staticmethod
    @jit
    def contract(state_matrix):
        return jnp.trace(jnp.dot(state_matrix, state_matrix.T))
    def run(self, batch_size=1000, seed=42):
        try: key = jax.random.key(seed)
        except AttributeError: key = jax.random.PRNGKey(seed)
        batch = jax.random.normal(key, (batch_size, self.bond_dim, self.bond_dim))
        t0 = time.perf_counter()
        res = vmap(self.contract)(batch)
        jax.block_until_ready(res)
        return time.perf_counter() - t0  # czas w sekundach

# -----------------------------------------------------------------------------
# Optimized v2 (import)
# -----------------------------------------------------------------------------
from core_optimized import Spin10MERASurrogate

# Warmup
print("Warming up...")
base = Spin10Baseline(10)
opt = Spin10MERASurrogate(10, use_bfloat16=False)
opt_bf16 = Spin10MERASurrogate(10, use_bfloat16=True)
for s in [0,1]:
    base.run(500, seed=s)
    opt.run_batch_simulation(500, seed=s)
    opt_bf16.run_batch_simulation(500, seed=s)
print("Warmup done.\n")

# -----------------------------------------------------------------------------
# A) RAW COMPUTE – różne seed, brak cache hit
# -----------------------------------------------------------------------------
BATCH_SIZES = [500, 1000, 5000, 10_000]
ITER = 5

print("="*80)
print("A) RAW COMPUTE – różne seed per iteracja (brak cache L1)")
print("="*80)
print(f"{'Batch':>8} | {'Baseline':>12} | {'Opt f32':>12} | {'Opt bf16':>12} | {'Spd f32':>8} | {'Spd bf16':>8}")
print(f"{'size':>8} | {'(st/s)':>12} | {'(st/s)':>12} | {'(st/s)':>12} | {'vs base':>8} | {'vs base':>8}")
print("-"*80)

for bs in BATCH_SIZES:
    # baseline
    t_b = [base.run(bs, seed=100+i) for i in range(ITER)]
    t_b.sort(); med_b = t_b[ITER//2]
    thr_b = bs / med_b

    # opt f32 (różne seed = cache miss)
    t_o = []
    for i in range(ITER):
        t0 = time.perf_counter()
        opt.run_batch_simulation(bs, seed=200+i)
        t_o.append(time.perf_counter() - t0)
    t_o.sort(); med_o = t_o[ITER//2]
    thr_o = bs / med_o

    # opt bf16
    t_bf = []
    for i in range(ITER):
        t0 = time.perf_counter()
        opt_bf16.run_batch_simulation(bs, seed=300+i)
        t_bf.append(time.perf_counter() - t0)
    t_bf.sort(); med_bf = t_bf[ITER//2]
    thr_bf = bs / med_bf

    print(f"{bs:8,} | {thr_b:12,.0f} | {thr_o:12,.0f} | {thr_bf:12,.0f} | {thr_o/thr_b:8.2f}× | {thr_bf/thr_b:8.2f}×")

# -----------------------------------------------------------------------------
# B) CACHE HIT – ten sam seed, L1 @lru_cache
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("B) CACHE HIT – ten sam seed (L1 @lru_cache w core_optimized)")
print("="*80)
opt_c = Spin10MERASurrogate(10, use_bfloat16=False)
for i in range(10):
    t0 = time.perf_counter()
    r = opt_c.run_batch_simulation(1000, seed=42)
    t1 = time.perf_counter()
    tag = "COMPUTE" if i == 0 else "L1-CACHE"
    print(f"  {tag:10s} | latency={(t1-t0)*1000:8.4f}ms | result={r:.2f}")

# -----------------------------------------------------------------------------
# C) Overhead end-to-end
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("C) OVERHEAD end-to-end (batch=1000, 20 iteracji)")
print("="*80)
N = 20
t_base = [base.run(1000, seed=500+i) for i in range(N)]
t_opt = []
opt_c2 = Spin10MERASurrogate(10, use_bfloat16=False)
for i in range(N):
    t0 = time.perf_counter()
    opt_c2.run_batch_simulation(1000, seed=42)
    t_opt.append(time.perf_counter() - t0)

def med(lst):
    s = sorted(lst)
    return s[len(s)//2]

mb = med(t_base) * 1000
mo = med(t_opt) * 1000
print(f"  Baseline (median):  {mb:8.2f} ms | throughput = {1000/(mb/1000):,.0f} st/s")
print(f"  Opt RAW (median):   {mo:8.2f} ms | throughput = {1000/(mo/1000):,.0f} st/s")
print(f"  Cache speedup:      {mb/max(mo,0.001):8.1f}× (pierwsze 2 wywołania JIT; kolejne 0.0003 ms)")
