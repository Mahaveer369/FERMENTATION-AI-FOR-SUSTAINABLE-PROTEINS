# Protein module
from app.protein.routes import router
from app.protein.analyzer import ProteinAnalyzer, ProteinAnalysisResult, protein_analyzer

__all__ = [
    "router",
    "ProteinAnalyzer",
    "ProteinAnalysisResult",
    "protein_analyzer"
]
