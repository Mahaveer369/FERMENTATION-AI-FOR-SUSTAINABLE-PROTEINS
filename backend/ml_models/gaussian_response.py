"""
FermaGen AI - Gaussian Response Model
Models biological optimum behavior for temperature and pH responses.
"""
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class GaussianParams:
    """Parameters for Gaussian response curve"""
    optimal: float  # Optimal value
    range_param: float  # Range/standard deviation
    min_response: float = 0.0  # Minimum response value
    max_response: float = 1.0  # Maximum response value


class GaussianResponseModel:
    """
    Gaussian response curve model for biological parameters.
    
    Models how biological systems respond to environmental conditions,
    peaking at optimal values and decreasing toward boundaries.
    
    Mathematical model:
    response = exp(-0.5 * ((value - optimal) / range_param)^2)
    """
    
    # Default profiles for microorganisms
    MICROBE_PROFILES = {
        "saccharomyces_cerevisiae": {
            "optimal_temp": 30.0,
            "temp_range": 8.0,
            "optimal_ph": 5.0,
            "ph_range": 1.5,
        },
        "escherichia_coli": {
            "optimal_temp": 37.0,
            "temp_range": 6.0,
            "optimal_ph": 7.0,
            "ph_range": 1.0,
        },
        "pichia_pastoris": {
            "optimal_temp": 28.0,
            "temp_range": 5.0,
            "optimal_ph": 5.5,
            "ph_range": 1.2,
        },
        "aspergillus_niger": {
            "optimal_temp": 30.0,
            "temp_range": 7.0,
            "optimal_ph": 4.5,
            "ph_range": 1.8,
        },
        "bacillus_subtilis": {
            "optimal_temp": 37.0,
            "temp_range": 8.0,
            "optimal_ph": 7.0,
            "ph_range": 1.5,
        },
    }
    
    def __init__(self, noise_factor: float = 0.05):
        """
        Initialize Gaussian Response Model.
        
        Args:
            noise_factor: Random noise factor (0-1) for realistic variation
        """
        self.noise_factor = noise_factor
    
    def calculate_response(
        self,
        value: float,
        optimal: float,
        range_param: float,
        add_noise: bool = True
    ) -> float:
        """
        Calculate Gaussian response for a given value.
        
        Args:
            value: Current parameter value
            optimal: Optimal parameter value
            range_param: Range/standard deviation
            add_noise: Whether to add random variation
        
        Returns:
            Response value between 0 and 1
        """
        # Gaussian curve calculation
        response = np.exp(-0.5 * ((value - optimal) / range_param) ** 2)
        
        # Add controlled noise for realism
        if add_noise:
            noise = np.random.normal(1.0, self.noise_factor)
            response = max(0, min(1.0, response * noise))
        
        return float(response)
    
    def calculate_temperature_response(
        self,
        temperature: float,
        microbe: str,
        add_noise: bool = True
    ) -> float:
        """
        Calculate temperature response for a specific microbe.
        
        Args:
            temperature: Temperature in Celsius
            microbe: Microbe identifier
            add_noise: Whether to add random variation
        
        Returns:
            Temperature response (0-1)
        """
        profile = self.MICROBE_PROFILES.get(
            microbe.lower().replace(" ", "_").replace("-", "_"),
            self.MICROBE_PROFILES["escherichia_coli"]
        )
        
        return self.calculate_response(
            temperature,
            profile["optimal_temp"],
            profile["temp_range"],
            add_noise
        )
    
    def calculate_ph_response(
        self,
        ph: float,
        microbe: str,
        add_noise: bool = True
    ) -> float:
        """
        Calculate pH response for a specific microbe.
        
        Args:
            ph: pH value
            microbe: Microbe identifier
            add_noise: Whether to add random variation
        
        Returns:
            pH response (0-1)
        """
        profile = self.MICROBE_PROFILES.get(
            microbe.lower().replace(" ", "_").replace("-", "_"),
            self.MICROBE_PROFILES["escherichia_coli"]
        )
        
        return self.calculate_response(
            ph,
            profile["optimal_ph"],
            profile["ph_range"],
            add_noise
        )
    
    def calculate_combined_response(
        self,
        temperature: float,
        ph: float,
        microbe: str,
        weights: Optional[Dict[str, float]] = None,
        add_noise: bool = True
    ) -> float:
        """
        Calculate combined temperature and pH response.
        
        Args:
            temperature: Temperature in Celsius
            ph: pH value
            microbe: Microbe identifier
            weights: Weights for temperature and pH (default: 0.5 each)
            add_noise: Whether to add random variation
        
        Returns:
            Combined response (0-1)
        """
        weights = weights or {"temperature": 0.5, "ph": 0.5}
        
        temp_response = self.calculate_temperature_response(
            temperature, microbe, add_noise=False
        )
        ph_response = self.calculate_ph_response(ph, microbe, add_noise=False)
        
        combined = (
            weights.get("temperature", 0.5) * temp_response +
            weights.get("ph", 0.5) * ph_response
        )
        
        if add_noise:
            noise = np.random.normal(1.0, self.noise_factor)
            combined = max(0, min(1.0, combined * noise))
        
        return float(combined)
    
    def find_optimal_range(
        self,
        microbe: str,
        param_type: str = "temperature",
        threshold: float = 0.8
    ) -> Tuple[float, float]:
        """
        Find the optimal range where response is above threshold.
        
        Args:
            microbe: Microbe identifier
            param_type: "temperature" or "ph"
            threshold: Minimum response threshold
        
        Returns:
            Tuple of (min_value, max_value) in the optimal range
        """
        profile = self.MICROBE_PROFILES.get(
            microbe.lower().replace(" ", "_").replace("-", "_"),
            self.MICROBE_PROFILES["escherichia_coli"]
        )
        
        if param_type == "temperature":
            optimal = profile["optimal_temp"]
            range_param = profile["temp_range"]
        else:
            optimal = profile["optimal_ph"]
            range_param = profile["ph_range"]
        
        # Calculate range where response >= threshold
        # threshold = exp(-0.5 * (x / range_param)^2)
        # log(threshold) = -0.5 * (x / range_param)^2
        # x = range_param * sqrt(-2 * log(threshold))
        delta = range_param * np.sqrt(-2 * np.log(threshold))
        
        return (optimal - delta, optimal + delta)
    
    def get_microbe_profile(self, microbe: str) -> Dict:
        """Get the profile for a specific microbe"""
        return self.MICROBE_PROFILES.get(
            microbe.lower().replace(" ", "_").replace("-", "_"),
            self.MICROBE_PROFILES["escherichia_coli"]
        )


# Singleton instance
gaussian_model = GaussianResponseModel()


def calculate_response(
    value: float,
    optimal: float,
    range_param: float,
    add_noise: bool = True
) -> float:
    """Convenience function for Gaussian response calculation"""
    return gaussian_model.calculate_response(value, optimal, range_param, add_noise)


def temperature_response(
    temperature: float,
    microbe: str,
    add_noise: bool = True
) -> float:
    """Convenience function for temperature response"""
    return gaussian_model.calculate_temperature_response(temperature, microbe, add_noise)


def ph_response(
    ph: float,
    microbe: str,
    add_noise: bool = True
) -> float:
    """Convenience function for pH response"""
    return gaussian_model.calculate_ph_response(ph, microbe, add_noise)
