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
