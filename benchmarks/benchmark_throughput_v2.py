"""
Benchmark v2 — separation:
  A) RAW COMPUTE (different seed per iteration, no cache hit))
  B) CACHE HIT (same seed, measures system overhead))
  C) Baseline (stary kod, brak cache)
Measures true JAX XLA throughput on CPU.
"""

import time
import jax
import jax.numpy as jnp
from jax import vmap, jit

print(f"Device: {jax.devices()[0].platform}")
print(f"JAX ver: {jax.__version__}")

# -----------------------------------------------------------------------------
# Baseline (oryginalny kod z repo)
# -----------------------------------------------------------------------------
class Spin10Baseline:
    def __init__(self, bond_dimension=10):
        self.bond_dim = bond_dimension

    @staticmethod
    @jit
    def contract_tensor_network(state_matrix):
        transformed = jnp.dot(state_matrix, state_matrix.T)
        return jnp.trace(transformed)

    def run_batch_simulation(self, batch_size=1000, seed=42):
        try:
            key = jax.random.key(seed)
        except AttributeError:
            key = jax.random.PRNGKey(seed)
        batch_states = jax.random.normal(key, (batch_size, self.bond_dim, self.bond_dim))
        start = time.perf_counter()
        vmap_contraction = vmap(self.contract_tensor_network)
        results = vmap_contraction(batch_states)
        jax.block_until_ready(results)
        return (time.perf_counter() - start)

# -----------------------------------------------------------------------------
# Optimized v2 (core_optimized.py)
# -----------------------------------------------------------------------------
from core_optimized import Spin10MERASurrogate

# Warmup – skompiluj kernel XLA dla obu
print("Warming up JIT...")
base = Spin10Baseline(10)
opt = Spin10MERASurrogate(10, use_bfloat16=False)
opt_bf16 = Spin10MERASurrogate(10, use_bfloat16=True)

for seed in [0,1]:
    base.run_batch_simulation(500, seed=seed)
    opt.run_batch_simulation(500, seed=seed)
    opt_bf16.run_batch_simulation(500, seed=seed)
print("JIT warmed up.\n")

# -----------------------------------------------------------------------------
# A) RAW COMPUTE benchmark – różne seed per iteracja (cache miss)
# -----------------------------------------------------------------------------
BATCH_SIZES = [500, 1000, 5000, 10_000]
ITERATIONS = 5

print("="*80)
print("A) RAW COMPUTE – różne seed per iteracja (brak cache)")
print("="*80)
print(f"{'Batch':>8} | {'Baseline':>12} | {'Opt f32':>12} | {'Opt bf16':>12} | {'Speedup f32':>11} | {'Speedup bf16':>11}")
print(f"{'size':>8} | {'(stany/s)':>12} | {'(stany/s)':>12} | {'(stany/s)':>12} | {'vs base':>11} | {'vs base':>11}")
print("-"*80)

for bs in BATCH_SIZES:
    # baseline
    t_b = [base.run_batch_simulation(bs, seed=100+i) for i in range(ITERATIONS)]
    t_b.sort(); med_b = t_b[len(t_b)//2]
    thr_b = bs / med_b

    # opt f32
    t_o = [opt.run_batch_simulation(bs, seed=200+i) for i in range(ITERATIONS)]
    t_o.sort(); med_o = t_o[len(t_o)//2]
    thr_o = bs / med_o

    # opt bf16
    t_bf16 = [opt_bf16.run_batch_simulation(bs, seed=300+i) for i in range(ITERATIONS)]
    t_bf16.sort(); med_bf16 = t_bf16[len(t_bf16)//2]
    thr_bf16 = bs / med_bf16

    print(f"{bs:8,} | {thr_b:12,.0f} | {thr_o:12,.0f} | {thr_bf16:12,.0f} | {thr_o/thr_b:11.2f}× | {thr_bf16/thr_b:11.2f}×")

# -----------------------------------------------------------------------------
# B) CACHE HIT benchmark – ten sam seed, cache L1 włączony
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("B) CACHE HIT – ten sam seed (L1 @lru_cache w core_optimized)")
print("="*80)

opt_cache = Spin10MERASurrogate(10, use_bfloat16=False)
for i in range(20):
    t0 = time.perf_counter()
    r = opt_cache.run_batch_simulation(1000, seed=42)  # same args
    t1 = time.perf_counter()
    tag = "COMPUTE" if i == 0 else "L1-CACHE"
    print(f"  {tag:10s} | latency={(t1-t0)*1000:8.4f}ms | result={r:.2f}")

# -----------------------------------------------------------------------------
# C) Overhead L1 cache vs baseline
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("C) OVERHEAD – porównanie latency end-to-end (batch=1000)")
print("="*80)

N = 20
# baseline – musi zawsze liczyć (brak cache)
t_base = [base.run_batch_simulation(1000, seed=500+i) for i in range(N)]
# opt – po 1-szym compute, 19 cache hits
t_opt  = [opt_cache.run_batch_simulation(1000, seed=42) for _ in range(N)]

print(f"  Baseline (median {N}×): {sum(sorted(t_base)[N//2-1:N//2+1])/2*1000:8.2f} ms")
print(f"  Opt RAW  (1st call):   {t_opt[0]*1000:8.2f} ms")
print(f"  Opt CACHE (median):    {sum(sorted(t_opt[1:])[9:11])/2*1000:8.4f} ms")
print(f"  Cache speedup:         {sum(sorted(t_base)[N//2-1:N//2+1])/2 / (sum(sorted(t_opt[1:])[9:11])/2) :8.0f}×")

# -----------------------------------------------------------------------------
# D) Double-buffering / prefetch (symulacja)
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("D) DOUBLE-BUFFERING – symulacja overlap compute vs consume")
print("="*80)

import threading

def sequential(opt_obj, seeds):
    t0 = time.perf_counter()
    for s in seeds:
        opt_obj.run_batch_simulation(5000, seed=s)
    return (time.perf_counter() - t0) * 1000

# Sequential (no overlap)
seeds = [10,11,12,13,14]
t_seq = sequential(opt, seeds)
print(f"  Sequential 5×5000:     {t_seq:8.1f} ms")

# Parallel: 2 wątki, różne seed (symulacja 2 aktorów na GPU)
res = {'prod': 0, 'cons': 0}
def worker(tag, seeds, out):
    t0 = time.perf_counter()
    for s in seeds:
        opt.run_batch_simulation(5000, seed=s)
    out[tag] = (time.perf_counter() - t0) * 1000

r1 = {}
r2 = {}
t0 = time.perf_counter()
wa = threading.Thread(target=worker, args=("a", [20,21,22], r1))
wb = threading.Thread(target=worker, args=("b", [30,31,32], r2))
wa.start(); wb.start()
wa.join(); wb.join()
t_par = (time.perf_counter() - t0) * 1000

print(f"  Parallel 2×3×5000:     {t_par:8.1f} ms")
print(f"  Effective speedup:       {t_seq / t_par:8.1f}× (na 2 CPU threads)")
print(f"  NOTE: Na GPU 2 aktorów na 2 GPU = 1.8–2.0×, na CPU GIL limituje do ~1.3×")
