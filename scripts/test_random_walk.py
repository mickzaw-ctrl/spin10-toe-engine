import networkx as nx  
from spectral_dimension_random_walk import RandomWalkSpectralDimension  
  
# Wygeneration potężnego grafu o skali holograficznej (np. 100 000 węzłów)  
wielki_graf = nx.barabasi_albert_graph(100000, 4)  
  
# Błyskawiczna simulation errorzenia losowego (20 000 errorzących, 150 stepów czasowych)  
t_vals, probs, d_S = RandomWalkSpectralDimension.exact_spectral_dimension_random_walk(  
    wielki_graf, max_steps=150, num_walkers=20000, lazy_prob=0.5  
)  
  
plateaux = RandomWalkSpectralDimension.compute_spectral_plateaux(t_vals, d_S)  
print(f"Wymiar w skali mikro (UV): d_S = {plateaux['d_S_UV']:.2f}")  
print(f"Wymiar w skali makro (IR): d_S = {plateaux['d_S_IR_numeric']:.2f}")
