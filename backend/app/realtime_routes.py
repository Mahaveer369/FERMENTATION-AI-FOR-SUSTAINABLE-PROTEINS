"""
FermaGen AI — Real-Time API Routes
===================================
FastAPI endpoints exposing the PubChem / UniProt / ESMFold pipeline.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.realtime_pipeline import (
    pubchem_get_substrate,
    uniprot_search_protein,
    uniprot_get_accession,
    uniprot_get_sequence,
    esmfold_predict_structure,
    run_fermentation_pipeline,
    verify_all_apis,
)

router = APIRouter()


# ── Request / Response models ──────────────────────────────────────

class StructurePredictionRequest(BaseModel):
    """Body for ESMFold structure prediction."""
    sequence: str = Field(
        ...,
        min_length=10,
        max_length=400,
        description="Amino-acid sequence (one-letter codes, max 400 residues)",
    )


class PipelineRequest(BaseModel):
    """Body for the full end-to-end pipeline."""
    substrate_name: str = Field("glucose", description="Fermentation substrate name")
    protein_name: str = Field("ovalbumin", description="Target protein name")
    organism: str = Field("Gallus gallus", description="Source organism")
    predict_structure: bool = Field(
        True,
        description="If True, call ESMFold (adds ~30-60 s)",
    )


# ── Endpoints ──────────────────────────────────────────────────────

@router.get("/substrate/{name}")
async def get_substrate(name: str):
    """
    Fetch molecular properties for a fermentation substrate from PubChem.

    Example: ``/realtime/substrate/glucose``
    """
    try:
        return pubchem_get_substrate(name)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"PubChem error: {exc}")


@router.get("/protein/search")
async def search_protein(
    query: str = Query(..., description="Protein name, e.g. 'ovalbumin'"),
    organism: Optional[str] = Query(None, description="Organism filter, e.g. 'Gallus gallus'"),
    limit: int = Query(5, ge=1, le=20),
):
    """
    Search UniProt for proteins by name and optional organism filter.

    Example: ``/realtime/protein/search?query=ovalbumin&organism=Gallus+gallus``
    """
    try:
        results = uniprot_search_protein(query, organism=organism, limit=limit)
        return {"query": query, "organism": organism, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"UniProt error: {exc}")


@router.get("/protein/sequence/{accession}")
async def get_protein_sequence(accession: str):
    """
    Retrieve the full amino-acid sequence for a UniProt accession.

    Example: ``/realtime/protein/sequence/P01012``
    """
    try:
        return uniprot_get_sequence(accession)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"UniProt error: {exc}")


@router.post("/structure/predict")
async def predict_structure(body: StructurePredictionRequest):
    """
    Submit a protein sequence to NVIDIA ESMFold for 3-D structure prediction.

    Returns PDB data and mean pLDDT confidence score.
    """
    try:
        return esmfold_predict_structure(body.sequence)
    except EnvironmentError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ESMFold error: {exc}")


@router.post("/pipeline")
async def full_pipeline(body: PipelineRequest):
    """
    Run the complete real-time data pipeline:
      PubChem → UniProt → ESMFold → Fermentation insights.

    This can take 30-60 seconds when ``predict_structure`` is enabled.
    """
    try:
        return run_fermentation_pipeline(
            substrate_name=body.substrate_name,
            protein_name=body.protein_name,
            organism=body.organism,
            predict_structure=body.predict_structure,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Pipeline error: {exc}")


@router.get("/verify")
async def verify_apis():
    """
    Health-check all three external APIs (PubChem, UniProt, ESMFold).

    Returns pass/fail status for each endpoint.
    """
    try:
        return verify_all_apis()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification error: {exc}")
