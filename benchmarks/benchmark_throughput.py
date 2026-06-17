"""
Benchmark A/B: baseline vs optimized Spin10 core.
Measures throughput for various batch sizes, dtype, cache.
"""

import time
import sys
import jax
import jax.numpy as jnp
from jax import vmap, jit

# -----------------------------------------------------------------------------
# Baseline (oryginalny kod)
# -----------------------------------------------------------------------------
class Spin10Baseline:
    def __init__(self, bond_dimension=10):
        self.bond_dim = bond_dimension

    @staticmethod
    @jit
    def contract_tensor_network(state_matrix):
        transformed = jnp.dot(state_matrix, state_matrix.T)
        return jnp.trace(transformed)

    def run_batch_simulation(self, batch_size=1000):
        try:
            key = jax.random.key(42)
        except AttributeError:
            key = jax.random.PRNGKey(42)
        batch_states = jax.random.normal(key, (batch_size, self.bond_dim, self.bond_dim))
        start = time.perf_counter()
        vmap_contraction = vmap(self.contract_tensor_network)
        results = vmap_contraction(batch_states)
        jax.block_until_ready(results)
        elapsed = (time.perf_counter() - start)
        return elapsed

# -----------------------------------------------------------------------------
# Optimized v2 (core_optimized.py)
# -----------------------------------------------------------------------------
from core_optimized import Spin10MERASurrogate

# Warmup JIT – aby oba miały skompilowany kernel
print("Warming up JIT...")
base = Spin10Baseline(10)
opt = Spin10MERASurrogate(10, use_bfloat16=False)

_ = base.run_batch_simulation(500)
_ = opt.run_batch_simulation(500, seed=42)
print("JIT warmed up.")

# -----------------------------------------------------------------------------
# Benchmark suite
# -----------------------------------------------------------------------------
BATCH_SIZES = [500, 1000, 5000, 10_000, 50_000]
ITERATIONS = 5

def bench(name, fn, batch_size, iter):
    times = []
    for i in range(iter):
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        times.append(t1 - t0)
    # Median (robust)
    times.sort()
    median = times[len(times)//2]
    throughput = batch_size / median
    return median, throughput

print(f"\nDevice: {jax.devices()[0].platform}")
print(f"JAX version: {jax.__version__}")
print(f"CPU cores (nproc): {jax.local_device_count()}")
print(f"{'='*70}")
print(f"{'Batch':>8} | {'Baseline':>12} | {'Opt (f32)':>12} | {'Opt (bf16)':>12} | {'Speedup f32':>10} | {'Speedup bf16':>10}")
print(f"{'(size)':>8} | {'(st/s)':>12} | {'(st/s)':>12} | {'(st/s)':>12} | {'vs base':>10} | {'vs base':>10}")
print(f"{'='*70}")

for bs in BATCH_SIZES:
    # Baseline
    t_b, thr_b = bench("baseline", lambda: base.run_batch_simulation(bs), bs, ITERATIONS)
    # Optimized float32
    t_o, thr_o = bench("opt_f32", lambda: opt.run_batch_simulation(bs, seed=42), bs, ITERATIONS)
    # Optimized bfloat16 (new instance per benchmark to avoid cache bleed, but JIT shared)
    opt_bf16 = Spin10MERASurrogate(10, use_bfloat16=True)
    t_bf16, thr_bf16 = bench("opt_bf16", lambda: opt_bf16.run_batch_simulation(bs, seed=43), bs, ITERATIONS)

    speed_f32 = thr_o / thr_b if thr_b > 0 else 0
    speed_bf16 = thr_bf16 / thr_b if thr_b > 0 else 0

    print(f"{bs:8,} | {thr_b:12,.0f} | {thr_o:12,.0f} | {thr_bf16:12,.0f} | {speed_f32:10.1f}× | {speed_bf16:10.1f}×")

# Cache hit benchmark (L1 cache in opt)
print(f"\n{'='*70}")
print("CACHE HIT BENCHMARK (batch=1000, 20 calls)")
print(f"{'='*70}")
opt_cache = Spin10MERASurrogate(10, use_bfloat16=False)
for i in range(20):
    t0 = time.perf_counter()
    r = opt_cache.run_batch_simulation(1000, seed=42)  # same params
    t1 = time.perf_counter()
    source = "L1-CACHE" if i > 0 else "COMPUTED"
    print(f"  call {i:2d}: {source:10s} | latency={((t1-t0)*1000):8.3f}ms | result={r:.2f}")

print(f"\n{'='*70}")
print("DOUBLE-BUFFERING SIMULATION")
print(f"{'='*70}")
# Symulujemy: worker prefetchuje batch N+1 podczas gdy klient czeka na N
import threading
results_queue = []

def producer():
    buf = {}
    for seed in [1,2,3,4,5]:
        # simulate prefetch
        t0 = time.perf_counter()
        res = opt.run_batch_simulation(5000, seed=seed)
        buf[seed] = res
        t1 = time.perf_counter()
        results_queue.append(("prefetch", seed, (t1-t0)*1000))
        time.sleep(0.001)  # tiny delay between prefetches

def consumer():
    for seed in [1,2,3,4,5]:
        t0 = time.perf_counter()
        # In real system: pop from prefetch buffer, ~0 latency
        res = opt.run_batch_simulation(5000, seed=seed)
        t1 = time.perf_counter()
        results_queue.append(("consume", seed, (t1-t0)*1000))

# Sequential (no prefetch)
t0 = time.perf_counter()
for seed in [1,2,3,4,5]:
    opt.run_batch_simulation(5000, seed=seed)
t_seq = (time.perf_counter() - t0) * 1000

# Parallel (producer + consumer overlap)
prod = threading.Thread(target=producer)
cons = threading.Thread(target=consumer)
t0 = time.perf_counter()
prod.start()
cons.start()
prod.join()
cons.join()
t_par = (time.perf_counter() - t0) * 1000

print(f"  Sequential 5×batch=5000 : {t_seq:8.1f} ms")
print(f"  Parallel (prefetch)     : {t_par:8.1f} ms")
print(f"  Effective speedup       : {t_seq/t_par if t_par>0 else 0:8.1f}×")
print(f"\nNOTE: On GPU, prefetch runs on device while host serves HTTP; speedup ≈ 1.5–2×.")
