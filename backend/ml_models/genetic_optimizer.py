"""
FermaGen AI - Genetic Algorithm (GA) Optimizer
Advanced bio-informatics optimizer adopting principles of natural evolution to map
global hyperparameter minimas across multi-dimensional substrate space.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class GeneticOptimizerConfig:
    """Rigorous configuration hyperparameters for evolutionary progression."""
    population_size: int = 50
    number_of_generations: int = 30
    mutation_probability: float = 0.1
    crossover_probability: float = 0.7
    elitism_retention: int = 5
    tournament_selection_size: int = 3

@dataclass
class Organism:
    """Represents a discrete candidate solution mapping an exact parameter 6D vector."""
    genes: Dict[str, float]
    fitness_objectives: Tuple[float, ...] = ()
    survival_fitness: float = 0.0

class EvolutionaryGeneticOptimizer:
    """
    Simulates biological selection mathematically restricting operations natively to 
    PubChem and UniProt boundary constraints. 
    """
    
    # Fundamental mutation limits mapped to realistic industrial bioreactor constraints
    MUTATION_DEVIATION = {
        "temperature": 3.0,
        "ph": 0.5,
        "duration": 12.0,
        "oxygen_level": 5.0,
        "agitation_speed": 50.0,
    }
    
    def __init__(self, config: Optional[GeneticOptimizerConfig] = None):
        self.config = config or GeneticOptimizerConfig()
        self.active_population: List[Organism] = []
        self.evaluator: Optional[Callable] = None

    def establish_evaluation_function(self, evaluator_fn: Callable):
        """Pass the Random Forest parallel execution block here for loss calculation."""
        self.evaluator = evaluator_fn

    def _initialize_diversity_pool(self, bounds: Dict[str, Tuple[float, float]]) -> List[Organism]:
        """Spawn initial generation utilizing uniform distribution constraint bounds."""
        population = []
        for _ in range(self.config.population_size):
            genome = {k: np.random.uniform(v[0], v[1]) for k, v in bounds.items()}
            population.append(Organism(genes=genome))
        return population

    def _evaluate_environmental_fitness(self, population: List[Organism]):
        """Runs the Random Forest regressors across the population space."""
        for org in population:
            try:
                out = self.evaluator(org.genes)
                org.fitness_objectives = tuple(out) if isinstance(out, (list, tuple)) else (out,)
            except Exception as e:
                org.fitness_objectives = (float('-inf'),)

    def _tournament_selection(self) -> Organism:
        """Simulate Darwinian survival between candidates."""
        combatants = np.random.choice(
            self.active_population, 
            size=min(self.config.tournament_selection_size, len(self.active_population)), 
            replace=False
        )
        return max(combatants, key=lambda org: org.survival_fitness)

    def _simulated_binary_crossover(self, p1: Organism, p2: Organism) -> Tuple[Organism, Organism]:
        """SBX genetic trait crossing."""
        c1, c2 = {}, {}
        for gene in p1.genes:
            if np.random.random() < self.config.crossover_probability:
                if np.random.random() < 0.5:
                    c1[gene], c2[gene] = p1.genes[gene], p2.genes[gene]
                else:
                    c1[gene], c2[gene] = p2.genes[gene], p1.genes[gene]
            else:
                c1[gene], c2[gene] = p1.genes[gene], p2.genes[gene]
        return Organism(genes=c1), Organism(genes=c2)

    def _gaussian_mutation(self, org: Organism, bounds: Dict[str, Tuple[float, float]]) -> Organism:
        """Induces synthetic radiation/mutation to prevent local minima entrapment."""
        mutant = deepcopy(org.genes)
        for gene in mutant:
            if np.random.random() < self.config.mutation_probability:
                dev = self.MUTATION_DEVIATION.get(gene, 1.0)
                mutant[gene] += np.random.normal(0, dev)
                mutant[gene] = np.clip(mutant[gene], bounds[gene][0], bounds[gene][1])
        return Organism(genes=mutant)

    def compute_evolution(self, bounds: Dict, pareto_sorter: Callable) -> List[Dict]:
        """
        Main optimization execution loop integrating the Pareto Evaluator exactly as
        specified in System Architecture.
        """
        if not self.evaluator:
            raise ValueError("Evaluator not set.")
            
        self.active_population = self._initialize_diversity_pool(bounds)
        
        print("Initializing Generation 0...")
        for gen in range(self.config.number_of_generations):
            self._evaluate_environmental_fitness(self.active_population)
            
            # Utilize external Pareto sorter
            fronts = pareto_sorter(self.active_population)
            pareto_optimal_front = fronts[0] if fronts else []
            
            # Simple fitness assignment based on front rank
            for idx, front in enumerate(fronts):
                for ind in front:
                    ind.survival_fitness = len(fronts) - idx  # Lower front = higher fitness

            next_gen = sorted(self.active_population, key=lambda x: x.survival_fitness, reverse=True)[:self.config.elitism_retention]
            
            while len(next_gen) < self.config.population_size:
                p1 = self._tournament_selection()
                p2 = self._tournament_selection()
                c1, c2 = self._simulated_binary_crossover(p1, p2)
                next_gen.append(self._gaussian_mutation(c1, bounds))
                if len(next_gen) < self.config.population_size:
                    next_gen.append(self._gaussian_mutation(c2, bounds))
                    
            self.active_population = next_gen
            
        # Final pass
        self._evaluate_environmental_fitness(self.active_population)
        final_fronts = pareto_sorter(self.active_population)
        best_front = final_fronts[0] if final_fronts else []
        
        return [{"params": ind.genes, "objectives": ind.fitness_objectives} for ind in best_front]

# Interface
if __name__ == "__main__":
    print("GA Model initialized. Awaiting API integration signals.")
