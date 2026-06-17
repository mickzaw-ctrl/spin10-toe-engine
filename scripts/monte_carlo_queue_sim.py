"""
Monte Carlo simulation kolejki priorytetowej CloudOrchestrator.
Generuje N tasks z losowymi priorytetami (1=CRITICAL, 5=BACKGROUND),
mierzy kolejność przetwarzania, cache hit ratio i czasy latency.
Analiza statystyczna w JAX.
"""

import time
import ray
import jax
import jax.numpy as jnp
from collections import defaultdict
from core import CloudOrchestrator

# -----------------------------------------------------------------------------
# Parametry symulacji
# -----------------------------------------------------------------------------
N = 200
SEED = 42
P_CRITICAL = 0.30           # 30% tasks Criticalch (priorytet 1)
BATCH_OPTIONS = [500, 1000, 2000]
CACHE_LIMIT = 100

# -----------------------------------------------------------------------------
# Inicjalizacja Ray
# -----------------------------------------------------------------------------
if not ray.is_initialized():
    ray.init(ignore_reinit_error=True)
else:
    print("Ray już zainicjalizowany – używam istniejącej instancji.")

actor = CloudOrchestrator.remote(cache_limit=CACHE_LIMIT)

# -----------------------------------------------------------------------------
# 1. Generacja tasks (JAX random)
# -----------------------------------------------------------------------------
key = jax.random.PRNGKey(SEED)
keys = jax.random.split(key, N * 2)

tasks_meta = []
print(f"Generuję {N} tasks...")

for i in range(N):
    k1, k2, *rest = keys[i*2:(i+1)*2]
    # Losuj priorytet: 1 (CRITICAL) lub 5 (BACKGROUND)
    is_critical = jax.random.uniform(k1) < P_CRITICAL
    priority = int(1 if is_critical else 5)
    # Losuj batch_size
    bs_idx = int(jax.random.randint(k2, (), 0, len(BATCH_OPTIONS)))
    batch_size = BATCH_OPTIONS[bs_idx]

    # Submit do aktora (mierzymy latency submitu)
    t0 = time.perf_counter()
    task_id = ray.get(actor.submit_task.remote(priority, {"batch_size": batch_size}))
    t1 = time.perf_counter()

    tasks_meta.append({
        "task_id": task_id,
        "priority": priority,
        "batch_size": batch_size,
        "submit_latency_ms": (t1 - t0) * 1000,
    })

# -----------------------------------------------------------------------------
# 2. Przetwarzanie kolejki (mierzymy kolejność i źródło wyniku)
# -----------------------------------------------------------------------------
print("Przetwarzanie kolejki...")
results = []
for order in range(N):
    t0 = time.perf_counter()
    res = ray.get(actor.process_next_task.remote())
    t1 = time.perf_counter()

    results.append({
        "order": order,                       # kolejność wykonania (0 = pierwszy)
        "process_latency_ms": (t1 - t0) * 1000,
        "status": res.get("status"),
        "source": res.get("source"),
        "task_id": res.get("task_id"),
        "result": res.get("result"),
        "message": res.get("message", ""),
    })

# -----------------------------------------------------------------------------
# 3. Mapowanie task_id -> oryginalny priorytet / batch_size
# -----------------------------------------------------------------------------
task_to_meta = {t["task_id"]: t for t in tasks_meta}
for r in results:
    meta = task_to_meta.get(r["task_id"], {})
    r["original_priority"] = meta.get("priority", -1)
    r["original_batch_size"] = meta.get("batch_size", -1)

# -----------------------------------------------------------------------------
# 4. Analiza statystyczna w JAX
# -----------------------------------------------------------------------------
# Arrays JAX
orders_j = jnp.array([r["order"] for r in results], dtype=jnp.float32)
priorities_j = jnp.array([r["original_priority"] for r in results])
sources_j = jnp.array([1 if r["source"] == "CACHE" else 0 for r in results])
proc_times_j = jnp.array([r["process_latency_ms"] for r in results], dtype=jnp.float32)

# Maski
mask_p1 = priorities_j == 1
mask_p5 = priorities_j == 5
mask_cache = sources_j == 1
mask_computed = sources_j == 0

# Statystyki kolejności
mean_order_p1 = float(jnp.mean(orders_j[mask_p1]))
mean_order_p5 = float(jnp.mean(orders_j[mask_p5]))
median_order_p1 = float(jnp.median(orders_j[mask_p1]))
median_order_p5 = float(jnp.median(orders_j[mask_p5]))

# Ile % priorytetów 1 wykonano w pierwszych 50 pozycjach?
first_50 = orders_j < 50
p1_in_first_50 = int(jnp.sum(mask_p1 & first_50))
total_p1 = int(jnp.sum(mask_p1))

# Cache hit ratio per priorytet
cache_p1 = int(jnp.sum(mask_p1 & mask_cache))
cache_p5 = int(jnp.sum(mask_p5 & mask_cache))
computed_p1 = int(jnp.sum(mask_p1 & mask_computed))
computed_p5 = int(jnp.sum(mask_p5 & mask_computed))

# Latency procesowania
mean_proc = float(jnp.mean(proc_times_j))
max_proc = float(jnp.max(proc_times_j))

# Różnica w kolejności (JAX)
order_diff = float(jnp.mean(orders_j[mask_p5]) - jnp.mean(orders_j[mask_p1]))

# -----------------------------------------------------------------------------
# 5. Raport
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("   MONTE CARLO – ANALIZA KOLEJKI PRIORYTETOWEJ")
print("=" * 60)

print(f"\n[PARAMETRY SYMUACJI]")
print(f"  Count tasks      : {N}")
print(f"  P(CRITICAL=1)   : {P_CRITICAL}")
print(f"  P(BACKGROUND=5) : {1 - P_CRITICAL}")
print(f"  Batch sizes     : {BATCH_OPTIONS}")
print(f"  Cache limit     : {CACHE_LIMIT}")

print(f"\n[SKŁAD tasks]")
print(f"  Zadania priorytet 1 (CRITICAL) : {total_p1} ({total_p1/N*100:.1f}%)")
print(f"  Zadania priorytet 5 (BACKGROUND): {N-total_p1} ({(N-total_p1)/N*100:.1f}%)")

print(f"\n[KOLEJNOŚĆ PRZETWARZANIA]")
print(f"  Średnia pozycja P=1 : {mean_order_p1:.1f} (mediana {median_order_p1:.0f})")
print(f"  Średnia pozycja P=5 : {mean_order_p5:.1f} (mediana {median_order_p5:.0f})")
print(f"  Przewaga P=1        : {order_diff:.1f} pozycji wcześniej")
print(f"  P=1 w TOP-50        : {p1_in_first_50}/{total_p1} ({p1_in_first_50/total_p1*100:.1f}%)")

print(f"\n[ŹRÓDŁO WYNIKU]")
print(f"  CACHE hits P=1 : {cache_p1}/{total_p1} ({cache_p1/total_p1*100:.1f}%)")
print(f"  CACHE hits P=5 : {cache_p5}/{N-total_p1} ({cache_p5/(N-total_p1)*100:.1f}%)")
print(f"  COMPUTED P=1   : {computed_p1}/{total_p1}")
print(f"  COMPUTED P=5   : {computed_p5}/{N-total_p1}")

print(f"\n[LATENCY PRZETWARZANIA]")
print(f"  Średni czas procesowania : {mean_proc:.2f} ms")
print(f"  Maksymalny czas          : {max_proc:.2f} ms")

print(f"\n[WERYFIKACJA HEAPQ]")
# Sprawdźmy czy wyniki są posortowane priorytetem
all_priorities = [r["original_priority"] for r in results]
is_strictly_sorted = all(all_priorities[i] <= all_priorities[i+1] for i in range(len(all_priorities)-1))
print(f"  Ścisłe sortowanie priorytetów : {is_strictly_sorted}")
if not is_strictly_sorted:
    # Znajdź pierwsze naruszenie
    for i in range(N-1):
        if all_priorities[i] > all_priorities[i+1]:
            print(f"  Pierwsze naruszenie: pozycja {i} (P={all_priorities[i]}) > pozycja {i+1} (P={all_priorities[i+1]})")
            print(f"    -> Wyjaśnienie: task P={all_priorities[i+1]} było w CACHE, więc przeskoczyło P={all_priorities[i]}")
            break

print(f"\n[DYSTRYBUCJA PRIORYTETÓW W KOLEJCE WYKONANIA]")
# Histogram pozycji per priorytet (20 segmentów)
bins = jnp.linspace(0, N, 21)
hist_p1, _ = jnp.histogram(orders_j[mask_p1], bins=bins)
hist_p5, _ = jnp.histogram(orders_j[mask_p5], bins=bins)
for i in range(20):
    lo, hi = int(bins[i]), int(bins[i+1])
    bar = "█" * int(hist_p1[i]) + "░" * int(hist_p5[i])
    print(f"  pozycje {lo:3d}-{hi:3d}  P=1:{int(hist_p1[i]):2d}  P=5:{int(hist_p5[i]):2d}  {bar}")

print("\n" + "=" * 60)
print("KONIEC SYMUACJI")
print("=" * 60)

# Zakończenie Raya
ray.shutdown()
