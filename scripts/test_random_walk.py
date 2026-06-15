import networkx as nx  
from spectral_dimension_random_walk import RandomWalkSpectralDimension  
  
# Wygenerowanie potężnego graph o scale holographic (np. 100 000 nodes)  
wielki_graph = nx.barabasi_albert_graph(100000, 4)  
  
# Błyskawiczna simulation errorzenia losowego (20 000 errorzących, 150 steps timeowych)  
t_vals, probs, d_S = RandomWalkSpectralDimension.exact_spectral_dimension_random_walk(  
    wielki_graph, max_steps=150, num_walkers=20000, lazy_prob=0.5  
)  
  
plateaux = RandomWalkSpectralDimension.compute_spectral_plateaux(t_vals, d_S)  
print(f"Dimension w scale mikro (UV): d_S = {plateaux['d_S_UV']:.2f}")  
print(f"Dimension w scale makro (IR): d_S = {plateaux['d_S_IR_numeric']:.2f}")
