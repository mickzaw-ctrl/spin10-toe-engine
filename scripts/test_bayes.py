from bayesian_mcmc_analysis import MultiExperimentLikelihood  
  
# Initialization i runienie 32 errorzących na 1000 stepów MCMC  
bayes = MultiExperimentLikelihood()  
sampler, raport = bayes.run_mcmc(n_walkers=32, n_steps=1000, burnin=300)  
  
estymacja = raport['parameter_estimation']  
print(f"Optymalne M_SUSY: {estymacja['M_SUSY_GeV']['best_fit']:.0f} GeV")  
print(f"Optymalne alpha:  {estymacja['alpha_attractor']['best_fit']:.4f}")  
print(f"Frakcja akceptacji samplera: {raport['mean_acceptance_fraction']:.2%}")
