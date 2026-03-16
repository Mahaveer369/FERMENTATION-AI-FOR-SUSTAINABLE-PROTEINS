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
        
        # Logistic function
        exponent = -growth_rate * (time - inflection_point)
        # Prevent overflow
        exponent = np.clip(exponent, -500, 500)
        
        growth = carrying_capacity / (1 + np.exp(exponent))
        
        if add_noise:
            noise = np.random.normal(1.0, self.noise_factor)
            growth = max(0, min(carrying_capacity, growth * noise))
        
        return float(growth)
    
    def calculate_specific_growth_rate(
        self,
        time: float,
        growth_rate: float,
        carrying_capacity: float = 1.0,
        inflection_point: float = None
    ) -> float:
        """
        Calculate specific growth rate (derivative of logistic).
        
        Args:
            time: Time in hours
            growth_rate: Growth rate constant
            carrying_capacity: Maximum normalized population
            inflection_point: Inflection point in hours
        
        Returns:
            Specific growth rate at time t
        """
        if inflection_point is None:
            inflection_point = self.default_inflection
        
        # Derivative of logistic function
        exp_term = np.exp(-growth_rate * (time - inflection_point))
        specific_rate = growth_rate * carrying_capacity * exp_term / (1 + exp_term) ** 2
        
        return float(specific_rate)
    
    def calculate_yield_factor(
        self,
        time: float,
        microbe: str,
        substrate: str = "glucose",
        add_noise: bool = True
    ) -> float:
        """
        Calculate yield factor based on growth.
        
        Args:
            time: Fermentation duration in hours
            microbe: Microbe identifier
            substrate: Substrate type
            add_noise: Whether to add random variation
        
        Returns:
            Yield factor (0-1)
        """
        # Get base growth rate for microbe
        base_rate = self.MICROBE_GROWTH_RATES.get(
            microbe.lower().replace(" ", "_").replace("-", "_"),
            0.4
        )
        
        # Apply substrate modifier
        substrate_mod = self.SUBSTRATE_MODIFIERS.get(
            substrate.lower().replace(" ", "_"),
            1.0
        )
        
        effective_rate = base_rate * substrate_mod
        
        return self.calculate_growth(
            time,
            effective_rate,
            carrying_capacity=1.0,
            inflection_point=self.default_inflection,
            add_noise=add_noise
        )
    
    def find_optimal_duration(
        self,
        microbe: str,
        substrate: str = "glucose",
        efficiency_threshold: float = 0.90
    ) -> float:
        """
        Find optimal fermentation duration for target efficiency.
        
        Args:
            microbe: Microbe identifier
            substrate: Substrate type
            efficiency_threshold: Target efficiency (0-1)
        
        Returns:
            Optimal duration in hours
        """
        base_rate = self.MICROBE_GROWTH_RATES.get(
            microbe.lower().replace(" ", "_").replace("-", "_"),
            0.4
        )
        
        substrate_mod = self.SUBSTRATE_MODIFIERS.get(
            substrate.lower().replace(" ", "_"),
            1.0
        )
        
        effective_rate = base_rate * substrate_mod
        
        # Solve for time when growth reaches threshold
        # growth = K / (1 + exp(-r * (t - t_inf))) = threshold * K
        # exp(-r * (t - t_inf)) = (K - threshold * K) / threshold * K
        # t = t_inf - (1/r) * ln((1/threshold) - 1)
        
        if efficiency_threshold >= 1.0:
            return 168.0  # 1 week max
        
        if efficiency_threshold <= 0:
            return 0.0
        
        ln_term = np.log((1 / efficiency_threshold) - 1)
        optimal_time = self.default_inflection - (ln_term / effective_rate)
        
        # Clamp to reasonable range
        return float(np.clip(optimal_time, 0, 168))
    
    def get_growth_phase(
        self,
        time: float,
        growth_rate: float,
        inflection_point: float = None
    ) -> str:
        """
        Determine the growth phase at given time.
        
        Args:
            time: Current time in hours
            growth_rate: Growth rate constant
            inflection_point: Inflection point in hours
        
        Returns:
            Growth phase: "lag", "exponential", "stationary", or "death"
        """
        if inflection_point is None:
            inflection_point = self.default_inflection
        
        # Calculate specific growth rate
        specific_rate = self.calculate_specific_rate(
            time, growth_rate, 1.0, inflection_point
        )
        
        if time < inflection_point * 0.5:
            return "lag"
        elif time < inflection_point * 1.5:
            return "exponential"
        elif time < inflection_point * 3:
            return "stationary"
        else:
            return "death"
    
    def simulate_growth_curve(
        self,
        duration: float,
        growth_rate: float,
        carrying_capacity: float = 1.0,
        inflection_point: float = None,
        num_points: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate complete growth curve.
        
        Args:
            duration: Total simulation time in hours
            growth_rate: Growth rate constant
            carrying_capacity: Maximum normalized population
            inflection_point: Inflection point in hours
            num_points: Number of time points
        
        Returns:
            Tuple of (times, growth_values) arrays
        """
        if inflection_point is None:
            inflection_point = self.default_inflection
        
        times = np.linspace(0, duration, num_points)
        growth_values = np.array([
            self.calculate_growth(
                t, growth_rate, carrying_capacity, inflection_point, add_noise=False
            )
            for t in times
        ])
        
        return times, growth_values
    
    def get_microbe_growth_rate(self, microbe: str) -> float:
        """Get the growth rate for a specific microbe"""
        return self.MICROBE_GROWTH_RATES.get(
            microbe.lower().replace(" ", "_").replace("-", "_"),
            0.4
        )
    
    def get_substrate_modifier(self, substrate: str) -> float:
        """Get the growth modifier for a specific substrate"""
        return self.SUBSTRATE_MODIFIERS.get(
            substrate.lower().replace(" ", "_"),
            1.0
        )


# Singleton instance
logistic_model = LogisticGrowthModel()


def calculate_growth(
    time: float,
    growth_rate: float,
    carrying_capacity: float = 1.0,
    inflection_point: float = 24.0,
    add_noise: bool = True
) -> float:
    """Convenience function for logistic growth calculation"""
    return logistic_model.calculate_growth(
        time, growth_rate, carrying_capacity, inflection_point, add_noise
    )


def yield_factor(
    time: float,
    microbe: str,
    substrate: str = "glucose",
    add_noise: bool = True
) -> float:
    """Convenience function for yield factor calculation"""
    return logistic_model.calculate_yield_factor(time, microbe, substrate, add_noise)
