"""
FermaGen AI - External API Routes
Endpoints for UniProt, KEGG, PubChem, and Nutrition data
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from app.external_apis import external_apis

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


# ========== UniProt Endpoints ==========

@router.get("/uniprot/search")
async def search_uniprot(
    query: str = Query(..., description="Search term for proteins"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Search UniProt for proteins
    
    Example: /external/uniprot/search?query=hemoglobin+human
    """
    results = await external_apis.search_uniprot(query, limit)
    return {"query": query, "results": results}


@router.get("/uniprot/protein/{accession}")
async def get_uniprot_protein(accession: str):
    """
    Get detailed protein info from UniProt by accession number
    
    Example: /external/uniprot/protein/P02144
    """
    result = await external_apis.get_uniprot_protein(accession)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ========== KEGG Endpoints ==========

@router.get("/kegg/pathways")
async def search_kegg_pathways(
    query: str = Query(..., description="Pathway name to search"),
    organism: str = Query("eco", description="KEGG organism code (eco=E.coli, sce=yeast)")
):
    """
    Search KEGG for metabolic pathways
    
    Example: /external/kegg/pathways?query=glycolysis&organism=sce
    
    Common organism codes:
    - eco: Escherichia coli
    - sce: Saccharomyces cerevisiae
    - bsu: Bacillus subtilis
    """
    results = await external_apis.search_kegg_pathway(query, organism)
    return {"query": query, "organism": organism, "pathways": results}


@router.get("/kegg/pathway/{pathway_id}")
async def get_kegg_pathway(pathway_id: str):
    """
    Get detailed pathway info from KEGG
    
    Example: /external/kegg/pathway/eco00010
    """
    result = await external_apis.get_kegg_pathway(pathway_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ========== PubChem Endpoints ==========

@router.get("/pubchem/search")
async def search_pubchem(
    name: str = Query(..., description="Compound name to search")
):
    """
    Search PubChem for chemical compounds
    
    Example: /external/pubchem/search?name=glucose
    """
    results = await external_apis.search_pubchem(name)
    return {"query": name, "compounds": results}


@router.get("/pubchem/compound/{cid}")
async def get_pubchem_compound(cid: int):
    """
    Get compound details from PubChem by CID
    
    Example: /external/pubchem/compound/5793
    """
    result = await external_apis.get_pubchem_compound(cid)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ========== Nutrition/Food Endpoints ==========

@router.get("/nutrition/search")
async def search_nutrition(
    query: str = Query(..., description="Food or ingredient to search"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Search Open Food Facts for nutrition data
    
    Example: /external/nutrition/search?query=soy+protein
    """
    results = await external_apis.search_usda_food(query, limit)
    return {"query": query, "foods": results}


# ========== Fermentation-Specific Endpoints ==========

@router.get("/substrate/{substrate_name}")
async def get_substrate_info(substrate_name: str):
    """
    Get chemical info about a fermentation substrate
    
    Example: /external/substrate/glucose
    """
    result = await external_apis.get_substrate_info(substrate_name)
    return result


@router.get("/microbe/{organism}/pathways")
async def get_microbe_pathways(
    organism: str,
    pathway_type: str = Query("fermentation", description="Type of pathway to search")
):
    """
    Get relevant metabolic pathways for a microorganism
    
    Example: /external/microbe/saccharomyces_cerevisiae/pathways
    
    Supported organisms:
    - saccharomyces_cerevisiae
    - escherichia_coli
    - pichia_pastoris
    - bacillus_subtilis
    - aspergillus_niger
    """
    results = await external_apis.get_microbe_pathways(organism, pathway_type)
    return {"organism": organism, "pathway_type": pathway_type, "pathways": results}
