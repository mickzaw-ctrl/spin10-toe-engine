from numerical_rge_solver import NumericalRGESolver  
  
# Calkowanie 2-petlowych RGE ze Split-SUSY na scale M_SUSY = 5 TeV (5000 GeV)  
t_vals, g_vals, a_gut, best_M_GUT = NumericalRGESolver.integrate_2loop_rge_flow(M_SUSY=5000.0)  
  
# Analysis punktu zbieznosci  
analysis = NumericalRGESolver.analyze_unification(t_vals, g_vals)  
print(f"Scale Unifikacji: M_GUT = {analysis['M_GUT_GeV']:.2e} GeV")  
print(f"Kat Weinberga sin^2(theta_W) = {analysis['sin2_theta_W_GUT']:.4f} (Docelowo: 0.375)")
