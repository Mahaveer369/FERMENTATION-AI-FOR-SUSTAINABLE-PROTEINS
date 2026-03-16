"""
FermaGen AI - Logistic Growth Model
Models microbial growth saturation using logistic growth curves.
"""
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class GrowthParams:
    """Parameters for logistic growth model"""
    growth_rate: float  # Maximum growth rate (per hour)
    carrying_capacity: float = 1.0  # Normalized carrying capacity
    inflection_point: float = 24.0  # Inflection point in hours


class LogisticGrowthModel:
    """
    Logistic growth model for microbial fermentation.
    
    Models microbial population growth with saturation kinetics,
    accounting for carrying capacity and growth rate limitations.
    
    Mathematical model:
    N(t) = K / (1 + exp(-r * (t - t_inf)))
    
    Where:
    - K = carrying capacity
    - r = growth rate
    - t_inf = inflection point
    """
    
    # Default growth rate profiles by microorganism (per hour)
    MICROBE_GROWTH_RATES = {
        "saccharomyces_cerevisiae": 0.4,
        "escherichia_coli": 0.5,
        "pichia_pastoris": 0.35,
        "aspergillus_niger": 0.3,
        "bacillus_subtilis": 0.45,
    }
    
    # Substrate-specific growth modifiers
    SUBSTRATE_MODIFIERS = {
        "glucose": 1.0,
        "sucrose": 0.95,
        "maltose": 0.90,
        "glycerol": 0.85,
        "methanol": 0.70,
        "lactose": 0.80,
        "starch": 0.65,
    }
    
    def __init__(
        self,
        default_inflection: float = 24.0,
        noise_factor: float = 0.05
    ):
        """
        Initialize Logistic Growth Model.
        
        Args:
            default_inflection: Default inflection point in hours
            noise_factor: Random noise factor for realistic variation
        """
        self.default_inflection = default_inflection
        self.noise_factor = noise_factor
    
    def calculate_growth(
        self,
        time: float,
        growth_rate: float,
        carrying_capacity: float = 1.0,
        inflection_point: float = None,
        add_noise: bool = True
    ) -> float:
        """
        Calculate logistic growth at given time.
        
        Args:
            time: Time in hours
            growth_rate: Growth rate constant (r)
            carrying_capacity: Maximum normalized population
            inflection_point: Inflection point in hours
            add_noise: Whether to add random variation
        
        Returns:
            Normalized growth (0 to carrying_capacity)
        """
        if inflection_point is None:
            inflection_point = self.default_inflection
        
