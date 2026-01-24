"""
FermaGen AI - External API Integrations
Connects to UniProt, KEGG, PubChem, and USDA APIs
"""
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import asyncio

from app.config import get_settings

settings = get_settings()


@dataclass
class UniProtProtein:
    """UniProt protein data"""
    accession: str
    name: str
    organism: str
    sequence: str
    length: int
    function: str = ""
    keywords: List[str] = None


@dataclass
class KEGGPathway:
    """KEGG pathway data"""
    pathway_id: str
    name: str
    organism: str
    genes: List[str] = None
    compounds: List[str] = None


@dataclass
class PubChemCompound:
    """PubChem compound data"""
    cid: int
    name: str
    molecular_formula: str
    molecular_weight: float
    iupac_name: str = ""
    smiles: str = ""


@dataclass
class USDANutrient:
    """USDA nutrient data"""
    fdc_id: int
    description: str
    protein_g: float
    carbs_g: float
    fat_g: float
    energy_kcal: float


class ExternalAPIs:
    """Client for external biotech and food APIs"""
    
    def __init__(self):
        self.uniprot_base = settings.uniprot_base_url
        self.kegg_base = settings.kegg_base_url
        self.pubchem_base = settings.pubchem_base_url
        self.usda_base = "https://api.nal.usda.gov/fdc/v1"
        self.timeout = 30.0
    
    # ========== UniProt API ==========
    
    async def search_uniprot(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search UniProt for proteins
        Example: search_uniprot("myoglobin human")
        """
        url = f"{self.uniprot_base}/uniprotkb/search"
        params = {
            "query": query,
            "format": "json",
            "size": limit,
            "fields": "accession,protein_name,organism_name,length,sequence"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data.get("results", []):
                    results.append({
                        "accession": entry.get("primaryAccession", ""),
                        "name": entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "Unknown"),
                        "organism": entry.get("organism", {}).get("scientificName", ""),
                        "length": entry.get("sequence", {}).get("length", 0),
                        "sequence": entry.get("sequence", {}).get("value", "")[:100] + "..."  # Truncate
                    })
                return results
            except Exception as e:
                return [{"error": str(e)}]
    
    async def get_uniprot_protein(self, accession: str) -> Dict:
        """
        Get detailed protein info from UniProt by accession
        Example: get_uniprot_protein("P02144")
        """
        url = f"{self.uniprot_base}/uniprotkb/{accession}"
        params = {"format": "json"}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "accession": data.get("primaryAccession", ""),
                    "name": data.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", ""),
                    "organism": data.get("organism", {}).get("scientificName", ""),
                    "sequence": data.get("sequence", {}).get("value", ""),
                    "length": data.get("sequence", {}).get("length", 0),
                    "function": self._extract_function(data),
                    "keywords": [kw.get("name", "") for kw in data.get("keywords", [])]
                }
            except Exception as e:
                return {"error": str(e)}
    
    def _extract_function(self, data: Dict) -> str:
        """Extract function description from UniProt data"""
        for comment in data.get("comments", []):
            if comment.get("commentType") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    return texts[0].get("value", "")
        return ""
    
    # ========== KEGG API ==========
    
    async def search_kegg_pathway(self, query: str, organism: str = "eco") -> List[Dict]:
        """
        Search KEGG for metabolic pathways
        Example: search_kegg_pathway("glycolysis", "sce")  # sce = S. cerevisiae
        """
        url = f"{self.kegg_base}/find/pathway/{query}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                results = []
                for line in response.text.strip().split("\n"):
                    if line:
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            pathway_id = parts[0].replace("path:", "")
                            name = parts[1]
                            results.append({
                                "pathway_id": pathway_id,
                                "name": name
                            })
                return results[:10]  # Limit results
            except Exception as e:
                return [{"error": str(e)}]
    
    async def get_kegg_pathway(self, pathway_id: str) -> Dict:
        """
        Get pathway details from KEGG
        Example: get_kegg_pathway("eco00010")  # Glycolysis in E. coli
        """
        url = f"{self.kegg_base}/get/{pathway_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                # Parse KEGG flat file format
                data = {"pathway_id": pathway_id, "genes": [], "compounds": []}
                current_section = None
                
                for line in response.text.split("\n"):
                    if line.startswith("NAME"):
                        data["name"] = line.replace("NAME", "").strip()
                    elif line.startswith("ORGANISM"):
                        data["organism"] = line.replace("ORGANISM", "").strip()
                    elif line.startswith("GENE"):
                        current_section = "genes"
                        gene = line.replace("GENE", "").strip().split()[0]
                        data["genes"].append(gene)
                    elif line.startswith("COMPOUND"):
                        current_section = "compounds"
                        compound = line.replace("COMPOUND", "").strip().split()[0]
                        data["compounds"].append(compound)
                    elif line.startswith(" ") and current_section:
                        item = line.strip().split()[0]
                        data[current_section].append(item)
                
                return data
            except Exception as e:
                return {"error": str(e)}
    
    # ========== PubChem API ==========
    
    async def search_pubchem(self, name: str) -> List[Dict]:
        """
        Search PubChem for compounds by name
        Example: search_pubchem("glucose")
        """
        url = f"{self.pubchem_base}/compound/name/{name}/cids/JSON"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                cids = data.get("IdentifierList", {}).get("CID", [])[:5]
                
                # Get details for each compound
                results = []
                for cid in cids:
                    compound = await self.get_pubchem_compound(cid)
                    if "error" not in compound:
                        results.append(compound)
                
                return results
            except Exception as e:
                return [{"error": str(e)}]
    
    async def get_pubchem_compound(self, cid: int) -> Dict:
        """
        Get compound details from PubChem by CID
        Example: get_pubchem_compound(5793)  # Glucose
        """
        url = f"{self.pubchem_base}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                props = data.get("PropertyTable", {}).get("Properties", [{}])[0]
                
                # Get common name
                name_url = f"{self.pubchem_base}/compound/cid/{cid}/synonyms/JSON"
                name_response = await client.get(name_url)
                names = name_response.json().get("InformationList", {}).get("Information", [{}])[0].get("Synonym", ["Unknown"])
                
                return {
                    "cid": cid,
                    "name": names[0] if names else "Unknown",
                    "molecular_formula": props.get("MolecularFormula", ""),
                    "molecular_weight": props.get("MolecularWeight", 0),
                    "iupac_name": props.get("IUPACName", ""),
                    "smiles": props.get("CanonicalSMILES", "")
                }
            except Exception as e:
                return {"error": str(e)}
    
    # ========== USDA FoodData Central API ==========
    
    async def search_usda_food(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search USDA FoodData Central for nutrition data
        Note: Requires API key for full access, using demo endpoint
        Example: search_usda_food("soy protein")
        """
        # Using Open Food Facts as free alternative
        url = f"https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": limit
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for product in data.get("products", []):
                    nutrients = product.get("nutriments", {})
                    results.append({
                        "name": product.get("product_name", "Unknown"),
                        "brand": product.get("brands", ""),
                        "protein_g": nutrients.get("proteins_100g", 0),
                        "carbs_g": nutrients.get("carbohydrates_100g", 0),
                        "fat_g": nutrients.get("fat_100g", 0),
                        "energy_kcal": nutrients.get("energy-kcal_100g", 0),
                        "categories": product.get("categories", "")
                    })
                return results
            except Exception as e:
                return [{"error": str(e)}]
    
    # ========== Fermentation-Specific Queries ==========
    
    async def get_substrate_info(self, substrate: str) -> Dict:
        """Get detailed info about a fermentation substrate from PubChem"""
        compounds = await self.search_pubchem(substrate)
        if compounds and "error" not in compounds[0]:
            return compounds[0]
        return {"name": substrate, "error": "Not found"}
    
    async def get_microbe_pathways(self, organism: str, pathway_type: str = "fermentation") -> List[Dict]:
        """Get relevant metabolic pathways for a microorganism"""
        # Map common names to KEGG organism codes
        organism_codes = {
            "saccharomyces_cerevisiae": "sce",
            "escherichia_coli": "eco",
            "pichia_pastoris": "ppa",
            "bacillus_subtilis": "bsu",
            "aspergillus_niger": "ang"
        }
        
        code = organism_codes.get(organism.lower(), "sce")
        pathways = await self.search_kegg_pathway(pathway_type, code)
        return pathways
    
    async def get_protein_from_uniprot(self, query: str) -> Dict:
        """Search and get first matching protein from UniProt"""
        results = await self.search_uniprot(query, limit=1)
        if results and "error" not in results[0]:
            accession = results[0].get("accession")
            if accession:
                return await self.get_uniprot_protein(accession)
        return {"error": "Protein not found"}


# Singleton instance
external_apis = ExternalAPIs()
