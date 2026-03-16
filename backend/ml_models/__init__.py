"""
FermaGen AI - ML Models Package
Standalone machine learning models for fermentation simulation and optimization.
"""

from .gaussian_response import GaussianResponseModel
from .logistic_growth import LogisticGrowthModel
from .genetic_optimizer import GeneticOptimizer
from .yield_predictor import YieldPredictor

__all__ = [
    "GaussianResponseModel",
    "LogisticGrowthModel", 
    "GeneticOptimizer",
    "YieldPredictor",
]

__version__ = "1.0.0"
