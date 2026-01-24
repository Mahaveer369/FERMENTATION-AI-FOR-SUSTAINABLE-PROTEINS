"""
FermaGen AI - Protein Analysis Routes
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Optional

from app.protein.analyzer import protein_analyzer, ProteinAnalysisResult

router = APIRouter()


class ProteinSequenceInput(BaseModel):
    """Input for protein analysis"""
    sequence: str = Field(..., min_length=1, description="Amino acid sequence (one-letter codes)")
    name: Optional[str] = Field(None, description="Optional sequence name")


class ProteinAnalysisResponse(BaseModel):
    """Response from protein analysis"""
    name: Optional[str]
    sequence_length: int
    molecular_weight: float
    molecular_weight_kda: float
    isoelectric_point: float
    hydrophobicity: float
    instability_index: float
    is_stable: bool
    aromaticity: float
    charge_at_ph7: float
    amino_acid_composition: Dict[str, float]
    secondary_structure_tendency: Dict[str, float]
    
    # Interpretation
    protein_type: str
    stability_class: str
    recommendations: str


@router.post("/analyze", response_model=ProteinAnalysisResponse)
async def analyze_protein(data: ProteinSequenceInput):
    """
    Analyze a protein sequence.
    
    Calculates:
    - Molecular weight
    - Isoelectric point (pI)
    - Amino acid composition
    - Hydrophobicity (GRAVY score)
    - Instability index
    - Secondary structure tendency
    """
    try:
        result = protein_analyzer.analyze(data.sequence)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Generate interpretations
    protein_type = _classify_protein(result)
    stability_class = "Stable" if result.is_stable else "Unstable"
    recommendations = _generate_recommendations(result)
    
    return ProteinAnalysisResponse(
        name=data.name,
        sequence_length=result.sequence_length,
        molecular_weight=result.molecular_weight,
        molecular_weight_kda=round(result.molecular_weight / 1000, 2),
        isoelectric_point=result.isoelectric_point,
        hydrophobicity=result.hydrophobicity,
        instability_index=result.instability_index,
        is_stable=result.is_stable,
        aromaticity=result.aromaticity,
        charge_at_ph7=result.charge_at_ph7,
        amino_acid_composition=result.amino_acid_composition,
        secondary_structure_tendency=result.secondary_structure_tendency,
        protein_type=protein_type,
        stability_class=stability_class,
        recommendations=recommendations
    )


def _classify_protein(result: ProteinAnalysisResult) -> str:
    """Classify protein based on properties"""
    if result.hydrophobicity > 0.5:
        return "Hydrophobic (membrane-associated)"
    elif result.hydrophobicity < -1.0:
        return "Highly hydrophilic (secreted/cytoplasmic)"
    elif result.isoelectric_point > 9:
        return "Basic protein"
    elif result.isoelectric_point < 5:
        return "Acidic protein"
    else:
        return "Neutral/globular protein"


def _generate_recommendations(result: ProteinAnalysisResult) -> str:
    """Generate fermentation recommendations based on protein properties"""
    recommendations = []
    
    if not result.is_stable:
        recommendations.append("Consider codon optimization for improved expression stability.")
    
    if result.hydrophobicity > 0:
        recommendations.append("Protein may aggregate; consider lower expression temperatures.")
    
    if result.molecular_weight > 50000:
        recommendations.append("Large protein - E. coli may have expression limitations; consider Pichia pastoris.")
    
    if result.isoelectric_point < 5:
        recommendations.append("Acidic protein - may require buffer optimization for downstream processing.")
    
    if result.aromaticity > 0.1:
        recommendations.append("High aromatic content - monitor for aggregation during expression.")
    
    if not recommendations:
        recommendations.append("Protein properties are favorable for standard expression systems.")
    
    return " ".join(recommendations)


@router.get("/amino-acids")
async def list_amino_acids():
    """List all amino acids with their properties"""
    from app.protein.analyzer import ProteinAnalyzer
    
    amino_acids = []
    aa_names = {
        'A': 'Alanine', 'R': 'Arginine', 'N': 'Asparagine', 'D': 'Aspartic acid',
        'C': 'Cysteine', 'E': 'Glutamic acid', 'Q': 'Glutamine', 'G': 'Glycine',
        'H': 'Histidine', 'I': 'Isoleucine', 'L': 'Leucine', 'K': 'Lysine',
        'M': 'Methionine', 'F': 'Phenylalanine', 'P': 'Proline', 'S': 'Serine',
        'T': 'Threonine', 'W': 'Tryptophan', 'Y': 'Tyrosine', 'V': 'Valine'
    }
    
    for code, weight in ProteinAnalyzer.AA_WEIGHTS.items():
        amino_acids.append({
            "code": code,
            "name": aa_names.get(code, "Unknown"),
            "molecular_weight": weight,
            "hydrophobicity": ProteinAnalyzer.HYDROPHOBICITY.get(code, 0)
        })
    
    return {"amino_acids": amino_acids}
