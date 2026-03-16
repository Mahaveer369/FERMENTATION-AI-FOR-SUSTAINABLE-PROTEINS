"""
FermaGen AI - Genetic Optimizer
Multi-objective genetic algorithm for fermentation parameter optimization.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class OptimizerConfig:
    """Configuration for genetic algorithm"""
    population_size: int = 50
    generations: int = 30
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    elite_count: int = 5
    tournament_size: int = 3


@dataclass
class OptimizationObjective:
    """Definition of an optimization objective"""
    name: str
    maximize: bool = True
    weight: float = 1.0
    target: Optional[float] = None


@dataclass
class Individual:
    """Individual solution in the population"""
    genes: Dict[str, float]
    objectives: Tuple[float, ...] = field(default_factory=tuple)
    fitness: float = 0.0
    dominated: bool = False
    domination_count: int = 0
    dominated_solutions: List['Individual'] = field(default_factory=list)
    
    def __hash__(self):
        return hash(frozenset(self.genes.items()))


class GeneticOptimizer:
    """
    Multi-objective Genetic Algorithm optimizer.
    
    Uses NSGA-II (Non-dominated Sorting Genetic Algorithm II) principles
    for multi-objective optimization of fermentation parameters.
    
    Objectives:
    - Maximize yield
    - Minimize duration (time)
    - Minimize CO2 footprint
    - Maximize sustainability
    """
    
    # Default parameter bounds
    DEFAULT_BOUNDS = {
        "temperature": (20, 45),
        "ph": (4, 8),
        "duration": (12, 96),
        "oxygen_level": (10, 40),
        "agitation_speed": (100, 400),
    }
    
    # Mutation standard deviations
    MUTATION_STD = {
        "temperature": 3.0,
        "ph": 0.5,
        "duration": 12.0,
        "oxygen_level": 5.0,
        "agitation_speed": 50.0,
    }
    
    def __init__(
        self,
        config: Optional[OptimizerConfig] = None,
        evaluator: Optional[Callable] = None
    ):
        """
        Initialize Genetic Optimizer.
        
        Args:
            config: Optimizer configuration
            evaluator: Function to evaluate individual solutions
        """
        self.config = config or OptimizerConfig()
        self.evaluator = evaluator
        self.population: List[Individual] = []
        self.pareto_front: List[Individual] = []
        self.best_solution: Optional[Individual] = None
        self.history: List[List[Individual]] = []
    
    def set_evaluator(self, evaluator: Callable):
        """Set the fitness evaluation function"""
        self.evaluator = evaluator
    
    def _initialize_population(
        self,
        bounds: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> List[Individual]:
        """Initialize random population within bounds"""
        bounds = bounds or self.DEFAULT_BOUNDS
        
        population = []
        for _ in range(self.config.population_size):
            genes = {
                key: np.random.uniform(bounds[key][0], bounds[key][1])
                for key in bounds
            }
            population.append(Individual(genes=genes))
        
        return population
    
    def _evaluate_population(self, population: List[Individual]) -> None:
        """Evaluate fitness for all individuals"""
        if self.evaluator is None:
            raise ValueError("No evaluator function set")
        
        for individual in population:
            try:
                objectives = self.evaluator(individual.genes)
                if isinstance(objectives, (list, tuple)):
                    individual.objectives = tuple(objectives)
                else:
                    individual.objectives = (objectives,)
            except Exception as e:
                print(f"Evaluation error: {e}")
                individual.objectives = (float('-inf'),)
    
    def _fast_non_dominated_sort(
        self,
        population: List[Individual]
    ) -> List[List[Individual]]:
        """Fast non-dominated sorting (NSGA-II)"""
        # Reset domination data
        for ind in population:
            ind.dominated = False
            ind.domination_count = 0
            ind.dominated_solutions = []
        
        fronts = [[]]
        
        # Find domination relationships
        for i, p in enumerate(population):
            for j, q in enumerate(population):
                if i == j:
                    continue
                
                if self._dominates(p.objectives, q.objectives):
                    p.dominated_solutions.append(q)
                elif self._dominates(q.objectives, p.objectives):
                    p.domination_count += 1
            
            if p.domination_count == 0:
                p.dominated = False
                fronts[0].append(p)
        
        # Create subsequent fronts
        current_front = 0
        while fronts[current_front]:
            next_front = []
            for p in fronts[current_front]:
                for q in p.dominated_solutions:
                    q.domination_count -= 1
                    if q.domination_count == 0:
                        q.dominated = False
                        next_front.append(q)
            
            current_front += 1
            if next_front:
                fronts.append(next_front)
        
        return [f for f in fronts if f]
    
    def _dominates(self, obj1: Tuple[float, ...], obj2: Tuple[float, ...]) -> bool:
        """Check if obj1 dominates obj2 (minimization assumed for all)"""
        at_least_one_better = False
        
        for a, b in zip(obj1, obj2):
            if a > b:  # Assuming minimization
                return False
            if a < b:
                at_least_one_better = True
        
        return at_least_one_better
    
    def _calculate_crowding_distance(
        self,
        front: List[Individual]
    ) -> None:
        """Calculate crowding distance for diversity preservation"""
        if len(front) <= 2:
            for ind in front:
                ind.fitness = float('inf')
            return
        
        # Initialize distances
        for ind in front:
            ind.fitness = 0.0
        
        # For each objective
        num_objectives = len(front[0].objectives)
        
        for obj_idx in range(num_objectives):
            # Sort by objective
            sorted_front = sorted(front, key=lambda x: x.objectives[obj_idx])
            
            # Boundary solutions get infinite distance
            sorted_front[0].fitness = float('inf')
            sorted_front[-1].fitness = float('inf')
            
            # Calculate range
            obj_range = (
                sorted_front[-1].objectives[obj_idx] -
                sorted_front[0].objectives[obj_idx]
            )
            
            if obj_range == 0:
                continue
            
            # Calculate crowding distance
            for i in range(1, len(sorted_front) - 1):
                sorted_front[i].fitness += (
                    sorted_front[i + 1].objectives[obj_idx] -
                    sorted_front[i - 1].objectives[obj_idx]
                ) / obj_range
    
    def _tournament_selection(
        self,
        population: List[Individual]
    ) -> Individual:
        """Tournament selection"""
        tournament = np.random.choice(
            population,
            size=min(self.config.tournament_size, len(population)),
            replace=False
        )
        
        # Prefer non-dominated solutions
        non_dominated = [t for t in tournament if not t.dominated]
        
        if non_dominated:
            return max(non_dominated, key=lambda x: x.fitness)
        
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(
        self,
        parent1: Individual,
        parent2: Individual
    ) -> Tuple[Individual, Individual]:
        """Simulated Binary Crossover (SBX)"""
        child1_genes = {}
        child2_genes = {}
        
        for key in parent1.genes:
            if np.random.random() < self.config.crossover_rate:
                # Uniform crossover
                if np.random.random() < 0.5:
                    child1_genes[key] = parent1.genes[key]
                    child2_genes[key] = parent2.genes[key]
                else:
                    child1_genes[key] = parent2.genes[key]
                    child2_genes[key] = parent1.genes[key]
            else:
                child1_genes[key] = parent1.genes[key]
                child2_genes[key] = parent2.genes[key]
        
        return Individual(genes=child1_genes), Individual(genes=child2_genes)
    
    def _mutate(
        self,
        individual: Individual,
        bounds: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> Individual:
        """Gaussian mutation"""
        bounds = bounds or self.DEFAULT_BOUNDS
        mutated_genes = deepcopy(individual.genes)
        
        for key in mutated_genes:
            if np.random.random() < self.config.mutation_rate:
                std = self.MUTATION_STD.get(key, 1.0)
                mutated_genes[key] += np.random.normal(0, std)
                
                # Clip to bounds
                mutated_genes[key] = np.clip(
                    mutated_genes[key],
                    bounds[key][0],
                    bounds[key][1]
                )
        
