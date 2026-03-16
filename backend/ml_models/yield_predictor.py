"""
FermaGen AI - Yield Predictor
ML model for predicting fermentation yield and related metrics.
"""
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class YieldInput:
    """Input parameters for yield prediction"""
    microbe_type: str
    substrate: str
    temperature: float
    ph: float
    duration: float
    oxygen_level: float = 21.0
    agitation_speed: float = 200.0


@dataclass
class YieldOutput:
    """Output from yield prediction"""
    predicted_yield: float
    energy_usage: float
    co2_footprint: float
    protein_score: float
    purity: float
    efficiency: float
    sustainability_score: float
    confidence: float


class YieldPredictor:
    """
    Machine Learning model for predicting fermentation yield and outcomes.
    
    Combines multiple sub-models:
    - Gaussian Response for temperature/pH effects
    - Logistic Growth for time-dependent yield
    - Metabolic models for energy and CO2
    
    Returns comprehensive predictions including:
    - Yield (g/L)
    - Energy consumption (kWh)
    - CO2 footprint (kg)
    - Protein quality score (0-100)
    - Purity (%)
    - Efficiency (%)
    - Sustainability score (0-100)
    """
    
    # Microbe profiles with optimal parameters
    MICROBE_PROFILES = {
        "saccharomyces_cerevisiae": {
            "optimal_temp": 30.0,
            "optimal_ph": 5.0,
            "temp_range": 8.0,
            "ph_range": 1.5,
            "max_yield": 45.0,
            "growth_rate": 0.4,
            "protein_potential": 85,
        },
        "escherichia_coli": {
            "optimal_temp": 37.0,
            "optimal_ph": 7.0,
            "temp_range": 6.0,
            "ph_range": 1.0,
            "max_yield": 35.0,
            "growth_rate": 0.5,
            "protein_potential": 80,
        },
        "pichia_pastoris": {
            "optimal_temp": 28.0,
            "optimal_ph": 5.5,
            "temp_range": 5.0,
            "ph_range": 1.2,
            "max_yield": 55.0,
            "growth_rate": 0.35,
            "protein_potential": 90,
        },
        "aspergillus_niger": {
            "optimal_temp": 30.0,
            "optimal_ph": 4.5,
            "temp_range": 7.0,
            "ph_range": 1.8,
            "max_yield": 40.0,
            "growth_rate": 0.3,
            "protein_potential": 75,
        },
        "bacillus_subtilis": {
            "optimal_temp": 37.0,
            "optimal_ph": 7.0,
            "temp_range": 8.0,
            "ph_range": 1.5,
            "max_yield": 30.0,
            "growth_rate": 0.45,
            "protein_potential": 78,
        },
    }
    
    # Substrate profiles
    SUBSTRATE_PROFILES = {
        "glucose": {"energy": 15.6, "conversion": 0.5, "co2_factor": 0.95},
        "sucrose": {"energy": 16.5, "conversion": 0.48, "co2_factor": 0.92},
        "maltose": {"energy": 15.8, "conversion": 0.45, "co2_factor": 0.88},
        "glycerol": {"energy": 17.6, "conversion": 0.55, "co2_factor": 0.75},
        "methanol": {"energy": 22.7, "conversion": 0.4, "co2_factor": 1.1},
        "lactose": {"energy": 15.4, "conversion": 0.42, "co2_factor": 0.85},
        "starch": {"energy": 17.0, "conversion": 0.35, "co2_factor": 0.82},
    }
    
    def __init__(self, noise_factor: float = 0.05):
        """
        Initialize Yield Predictor.
        
        Args:
            noise_factor: Random noise factor for realistic variation
        """
        self.noise_factor = noise_factor
    
    def _normalize_microbe(self, name: str) -> str:
        """Normalize microbe name"""
        normalized = name.lower().replace(" ", "_").replace("-", "_")
        if normalized in self.MICROBE_PROFILES:
            return normalized
        return "escherichia_coli"
    
    def _normalize_substrate(self, name: str) -> str:
        """Normalize substrate name"""
        normalized = name.lower().replace(" ", "_")
        if normalized in self.SUBSTRATE_PROFILES:
            return normalized
        return "glucose"
    
    def _gaussian_response(
        self,
        value: float,
        optimal: float,
        range_param: float
    ) -> float:
        """Calculate Gaussian response"""
        return np.exp(-0.5 * ((value - optimal) / range_param) ** 2)
    
    def _logistic_growth(
        self,
        duration: float,
        growth_rate: float
    ) -> float:
        """Calculate logistic growth factor"""
        k = 1.0
        return k / (1 + np.exp(-growth_rate * (duration - 24)))
    
    def predict_yield(
        self,
        params: YieldInput,
        add_noise: bool = True
    ) -> Tuple[float, float]:
        """
        Predict fermentation yield.
        
        Args:
            params: Input parameters
            add_noise: Whether to add random variation
        
        Returns:
            Tuple of (yield_g_per_L, confidence)
        """
        microbe = self._normalize_microbe(params.microbe_type)
        substrate = self._normalize_substrate(params.substrate)
        
        profile = self.MICROBE_PROFILES[microbe]
        substrate_profile = self.SUBSTRATE_PROFILES[substrate]
        
        # Temperature response
        temp_factor = self._gaussian_response(
            params.temperature,
            profile["optimal_temp"],
            profile["temp_range"]
        )
        
        # pH response
        ph_factor = self._gaussian_response(
            params.ph,
            profile["optimal_ph"],
            profile["ph_range"]
        )
        
        # Time factor (logistic growth)
        time_factor = self._logistic_growth(
            params.duration,
            profile["growth_rate"]
        )
        
        # Oxygen effect
        oxygen_factor = min(1.0, params.oxygen_level / 21.0)
        
        # Agitation effect
        agitation_factor = self._gaussian_response(
            params.agitation_speed, 200, 100
        )
        
        # Substrate conversion
        substrate_factor = substrate_profile["conversion"]
        
        # Calculate base yield
        max_yield = profile["max_yield"]
        base_yield = (
            max_yield * temp_factor * ph_factor * time_factor *
            oxygen_factor * agitation_factor * substrate_factor
        )
        
        # Add noise
        if add_noise:
            noise = np.random.normal(1.0, self.noise_factor)
            base_yield = max(0, base_yield * noise)
        
        # Confidence based on optimal conditions
        confidence = 0.7 + 0.3 * (temp_factor * ph_factor * oxygen_factor)
        
        return float(base_yield), float(np.clip(confidence, 0, 1))
    
    def predict_energy(
        self,
        params: YieldInput,
        predicted_yield: float,
        add_noise: bool = True
    ) -> float:
        """
        Predict energy consumption.
        
        Args:
            params: Input parameters
            predicted_yield: Predicted yield in g/L
            add_noise: Whether to add random variation
        
        Returns:
            Energy usage in kWh
        """
        # Base energy
        base_energy = 0.5
        
        # Agitation energy
        agitation_energy = (
            params.duration / 24 * params.agitation_speed / 200 * 0.8
        )
        
        # Temperature control energy
        temp_diff = abs(params.temperature - 25)
        temp_energy = params.duration / 24 * temp_diff / 10 * 0.3
        
        # Aeration energy
        aeration_energy = (
            params.oxygen_level / 21 * params.duration / 24 * 0.2
        )
        
        total_energy = base_energy + agitation_energy + temp_energy + aeration_energy
        
        if add_noise:
            noise = np.random.normal(1.0, self.noise_factor)
            total_energy = max(0.1, total_energy * noise)
        
        return float(total_energy)
    
    def predict_co2(
        self,
        params: YieldInput,
        predicted_yield: float,
        energy_usage: float,
        add_noise: bool = True
    ) -> float:
        """
        Predict CO2 footprint.
        
        Args:
            params: Input parameters
            predicted_yield: Predicted yield in g/L
            energy_usage: Energy usage in kWh
            add_noise: Whether to add random variation
        
        Returns:
            CO2 footprint in kg
        """
        substrate = self._normalize_substrate(params.substrate)
        substrate_profile = self.SUBSTRATE_PROFILES[substrate]
        
        # Metabolic CO2
        metabolic_co2 = predicted_yield * substrate_profile["co2_factor"] * 0.05
        
        # Energy CO2 (grid emission factor ~0.4 kg/kWh)
        energy_co2 = energy_usage * 0.4
        
        # Processing overhead
        processing_co2 = 0.1
        
        total_co2 = metabolic_co2 + energy_co2 + processing_co2
        
        if add_noise:
            noise = np.random.normal(1.0, self.noise_factor)
            total_co2 = max(0.01, total_co2 * noise)
        
        return float(total_co2)
    
    def predict_protein_score(
        self,
        params: YieldInput,
        predicted_yield: float,
        add_noise: bool = True
    ) -> float:
        """
        Predict protein quality score.
        
        Args:
            params: Input parameters
            predicted_yield: Predicted yield in g/L
            add_noise: Whether to add random variation
        
        Returns:
            Protein score (0-100)
        """
        microbe = self._normalize_microbe(params.microbe_type)
        profile = self.MICROBE_PROFILES[microbe]
        
        # Base score from microbe potential
        base_score = profile["protein_potential"]
        
        # Condition factors
        temp_factor = self._gaussian_response(
            params.temperature,
            profile["optimal_temp"],
            profile["temp_range"]
        )
        ph_factor = self._gaussian_response(
            params.ph,
            profile["optimal_ph"],
            profile["ph_range"]
        )
        
        # Yield factor
        yield_factor = min(1.0, predicted_yield / profile["max_yield"])
        
        # Calculate final score
        condition_modifier = (temp_factor * ph_factor * yield_factor) ** 0.5
        protein_score = base_score * condition_modifier
        
        if add_noise:
            noise = np.random.normal(1.0, self.noise_factor / 2)
            protein_score = max(0, min(100, protein_score * noise))
        
        return float(np.clip(protein_score, 0, 100))
    
    def calculate_sustainability_score(
        self,
        predicted_yield: float,
        energy_usage: float,
        co2_footprint: float
    ) -> float:
        """
        Calculate sustainability score.
        
        Args:
            predicted_yield: Yield in g/L
            energy_usage: Energy in kWh
            co2_footprint: CO2 in kg
        
        Returns:
            Sustainability score (0-100)
        """
        # Yield score
        yield_score = min(100, predicted_yield / 50 * 100)
        
        # Energy efficiency (kWh per gram)
        if predicted_yield > 0:
            energy_per_yield = energy_usage / predicted_yield
            energy_score = max(0, 100 - energy_per_yield * 50)
        else:
            energy_score = 0
        
        # CO2 efficiency (kg per gram)
        if predicted_yield > 0:
            co2_per_yield = co2_footprint / predicted_yield
            co2_score = max(0, 100 - co2_per_yield * 100)
        else:
            co2_score = 0
        
        # Weighted average
        sustainability = yield_score * 0.3 + energy_score * 0.35 + co2_score * 0.35
        
        return float(np.clip(sustainability, 0, 100))
    
    def predict(
        self,
        params: YieldInput,
        add_noise: bool = True
    ) -> YieldOutput:
        """
        Run complete yield prediction.
        
        Args:
            params: Input parameters
            add_noise: Whether to add random variation
        
        Returns:
            Complete prediction results
        """
        # Predict yield and confidence
        predicted_yield, confidence = self.predict_yield(params, add_noise)
        
        # Predict energy
        energy_usage = self.predict_energy(params, predicted_yield, add_noise)
        
        # Predict CO2
        co2_footprint = self.predict_co2(
            params, predicted_yield, energy_usage, add_noise
        )
        
        # Predict protein score
        protein_score = self.predict_protein_score(
            params, predicted_yield, add_noise
        )
        
        # Calculate derived metrics
        microbe = self._normalize_microbe(params.microbe_type)
        profile = self.MICROBE_PROFILES[microbe]
        
        efficiency = min(100, predicted_yield / profile["max_yield"] * 100)
        purity = min(100, 70 + protein_score / 100 * 30)
        
        # Calculate sustainability score
        sustainability_score = self.calculate_sustainability_score(
            predicted_yield, energy_usage, co2_footprint
        )
        
        return YieldOutput(
            predicted_yield=round(predicted_yield, 2),
            energy_usage=round(energy_usage, 2),
            co2_footprint=round(co2_footprint, 3),
            protein_score=round(protein_score, 1),
            purity=round(purity, 1),
            efficiency=round(efficiency, 1),
            sustainability_score=round(sustainability_score, 1),
            confidence=round(confidence, 2)
        )
    
    def get_microbe_profile(self, microbe: str) -> Dict:
        """Get profile for a specific microbe"""
        return self.MICROBE_PROFILES.get(
            self._normalize_microbe(microbe),
            self.MICROBE_PROFILES["escherichia_coli"]
        )
    
    def get_substrate_profile(self, substrate: str) -> Dict:
        """Get profile for a specific substrate"""
        return self.SUBSTRATE_PROFILES.get(
            self._normalize_substrate(substrate),
            self.SUBSTRATE_PROFILES["glucose"]
        )


# Singleton instance
yield_predictor = YieldPredictor()


def predict_yield(
    microbe_type: str,
    substrate: str,
    temperature: float,
    ph: float,
    duration: float,
    oxygen_level: float = 21.0,
    agitation_speed: float = 200.0,
    add_noise: bool = True
) -> YieldOutput:
    """
    Convenience function for yield prediction.
    
    Args:
        microbe_type: Microorganism type
        substrate: Carbon source
        temperature: Temperature in Celsius
        ph: pH level
        duration: Fermentation duration in hours
        oxygen_level: Oxygen level (%)
        agitation_speed: Agitation speed (RPM)
        add_noise: Whether to add random variation
    
    Returns:
        Prediction results
    """
    params = YieldInput(
        microbe_type=microbe_type,
        substrate=substrate,
        temperature=temperature,
        ph=ph,
        duration=duration,
        oxygen_level=oxygen_level,
        agitation_speed=agitation_speed
    )
    
    return yield_predictor.predict(params, add_noise)
