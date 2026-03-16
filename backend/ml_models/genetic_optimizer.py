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
