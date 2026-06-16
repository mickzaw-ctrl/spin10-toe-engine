import sys
import os
import ctypes
import time

def test_pure_cpp_kernel():
    print("="*75)
    print(" BEZPOSREDNI TEST JADRA W CZYSTYM C++ (libspin10_hpc.so)")
    print("="*75)
    
    # Sciezka do skompilowanej biblioteki
    so_path = os.path.join(os.path.dirname(__file__), '../src/hpc/libspin10_hpc.so')
    
    if not os.path.exists(so_path):
        print(f"[Error] Library {so_path} nie istnieje. Kopiowanie/Kompilacja...")
        return

    # Ladowanie biblioteki
    lib = ctypes.CDLL(so_path)
    lib.relax_spin10_links_cpp.argtypes = [
        ctypes.c_int, ctypes.c_int, ctypes.c_double,
        ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)
    ]
    lib.relax_spin10_links_cpp.restype = ctypes.c_int
    
    n_links = 1000000  # 1 milion matrixowych Link Variables 10x10
    n_sweeps = 10      # 10 pelnych iteracji przez wszystkie edges (10 milionow obrotow SO10!)
    beta = 2.5
    
    out_wloop = ctypes.c_double(0.0)
    out_action = ctypes.c_double(0.0)
    
    print(f"Running batched mnozen 10x10 w czystym C++ (Bez interpretera Pythona)...")
    print(f"Siatka: {n_links:,} edges, Rotacje: {n_sweeps} przejsc (Suma operacji: {n_links * n_sweeps:,}).")
    
    t0 = time.time()
    lib.relax_spin10_links_cpp(
        n_links, n_sweeps, beta, ctypes.byref(out_wloop), ctypes.byref(out_action)
    )
    dt = time.time() - t0
    
    # 100 operacji FLOPS na jedne mnozenie matrixowe
    total_flops = n_links * n_sweeps * 100
    gflops = (total_flops / dt) / 1e9
    
    print(f"\nResults z jadra C++:")
    print(f" - Wykonano w timeie:        {dt:.4f} s.")
    print(f" - Asymptotyczna Petla <W>:  {out_wloop.value:.4f}")
    print(f" - Wyznaczone Dzialanie YM:  {out_action.value:.2f}")
    print(f" - Rzeczywista Przepustowosc: {gflops:.2f} Giga-FLOPS (Miliardow FLOPS / s) !!!")
    print("="*75)

if __name__ == "__main__":
    test_pure_cpp_kernel()
