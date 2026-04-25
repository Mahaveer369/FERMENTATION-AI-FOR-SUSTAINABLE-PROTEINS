"""
FermaGen AI - Experiment Routes
API endpoints for fermentation experiments
"""
import logging

# Configure logger
logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database.database import get_db, User, Experiment, Result
from app.auth.utils import get_current_user
from app.experiments.schemas import (
    ExperimentCreate,
    ExperimentResponse,
    ResultResponse,
    ExperimentWithResult,
    ExperimentListResponse,
    MicrobeInfo,
    SubstrateInfo,
    FoodTypeInfo,
    MicrobeWithFoodContext,
    SubstrateWithFoodContext
)
from app.experiments.simulation import (
    FermentationSimulator,
    FermentationParams,
    run_simulation
)
from app.realtime_pipeline import run_fermentation_pipeline

router = APIRouter()
simulator = FermentationSimulator()


# Food type mappings with related microbes and substrates
FOOD_TYPE_DATA = {
    "milk_products": {
        "name": "milk_products",
        "display_name": "Milk & Dairy Products",
        "description": "Milk, cheese, yogurt, and other dairy-based substrates",
        "icon": "🥛",
        "related_microbes": [
            "lactobacillus_casei",
            "streptococcus_thermophilus",
            "propionibacterium_freudenreichii",
            "lactobacillus_rhamnosus",
            "lactobacillus_acidophilus",
            "bifidobacterium_bifidum",
            "enterococcus_faecium"
        ],
        "related_substrates": [
            "lactose",
            "milk_serum",
            "whey",
            "casein",
            "skim_milk"
        ]
    },
    "bread_grains": {
        "name": "bread_grains",
        "display_name": "Bread & Grains",
        "description": "Wheat, rice, maize, and cereal-based substrates",
        "icon": "🍞",
        "related_microbes": [
            "lactobacillus_plantarum",
            "bacillus_subtilis",
            "saccharomyces_cerevisiae",
            "aspergillus_niger",
            "bacillus_licheniformis"
        ],
        "related_substrates": [
            "glucose",
            "sucrose",
            "maltose",
            "starch",
            "wheat_bran",
            "rice_bran"
        ]
    },
    "legumes": {
        "name": "legumes",
        "display_name": "Legumes & Pulses",
        "description": "Soybean, lentils, chickpeas, and legume-based substrates",
        "icon": "🫘",
        "related_microbes": [
            "lactobacillus_plantarum",
            "bacillus_subtilis",
            "bacillus_licheniformis",
            "escherichia_coli",
            "corynebacterium_glutamicum"
        ],
        "related_substrates": [
            "glucose",
            "sucrose",
            "soy_protein",
            "legume_extract"
        ]
    },
    "vegetables": {
        "name": "vegetables",
        "display_name": "Vegetables & Plant Materials",
        "description": "Fruit peels, vegetable waste, and plant-based substrates",
        "icon": "🥬",
        "related_microbes": [
            "lactobacillus_plantarum",
            "aspergillus_niger",
            "pseudomonas_fluorescens",
            "bacillus_subtilis"
        ],
        "related_substrates": [
            "glucose",
            "fructose",
            "sucrose",
            "pectin",
            "cellulose"
        ]
    },
    "meat_fish": {
        "name": "meat_fish",
        "display_name": "Meat & Fish",
        "description": "Protein-rich substrates from animal sources",
        "icon": "🐟",
        "related_microbes": [
            "pseudomonas_fluorescens",
            "micrococcus_luteus",
            "enterococcus_faecium",
            "bacillus_subtilis"
        ],
        "related_substrates": [
            "peptone",
            "yeast_extract",
            "meat_extract",
            "fish_hydrolysate"
        ]
    },
    "fermented_foods": {
        "name": "fermented_foods",
        "display_name": "Fermented Foods",
        "description": "Traditional fermented food substrates like kimchi, sauerkraut",
        "icon": "🥒",
        "related_microbes": [
            "lactobacillus_plantarum",
            "lactobacillus_casei",
            "lactobacillus_rhamnosus",
            "lactobacillus_acidophilus",
            "pediococcus_acidilactici"
        ],
        "related_substrates": [
            "glucose",
            "sucrose",
            "vegetable_extract",
            "salt_brine"
        ]
    },
    "oilseed_cakes": {
        "name": "oilseed_cakes",
        "display_name": "Oilseed Cakes & Residues",
        "description": "Byproducts from oil extraction like groundnut, sunflower",
        "icon": "🌻",
        "related_microbes": [
            "bacillus_subtilis",
            "bacillus_licheniformis",
            "aspergillus_niger",
            "corynebacterium_glutamicum"
        ],
        "related_substrates": [
            "groundnut_cake",
            "sunflower_cake",
            "soybean_meal",
            "cottonseed_meal"
        ]
    },
    "agro_waste": {
        "name": "agro_waste",
        "display_name": "Agricultural Waste",
        "description": "Crop residues, bran, and agricultural byproducts",
        "icon": "🌾",
        "related_microbes": [
            "bacillus_licheniformis",
            "aspergillus_niger",
            "clostridium_butyricum",
            "lactobacillus_plantarum"
        ],
        "related_substrates": [
            "wheat_bran",
            "rice_bran",
            "corn_stover",
            "sugarcane_bagasse",
            "molasses"
        ]
    },
    "dairy_waste": {
        "name": "dairy_waste",
        "display_name": "Dairy Waste & Byproducts",
        "description": "Whey, lactose-rich waste from dairy processing",
        "icon": "🧀",
        "related_microbes": [
            "lactobacillus_casei",
            "streptococcus_thermophilus",
            "propionibacterium_freudenreichii",
            "escherichia_coli",
            "lactobacillus_acidophilus"
        ],
        "related_substrates": [
            "whey",
            "lactose",
            "milk_serum",
            "buttermilk"
        ]
    },
    "sugar_waste": {
        "name": "sugar_waste",
        "display_name": "Sugar Industry Waste",
        "description": "Molasses, syrups, and sugar processing byproducts",
        "icon": "🍬",
        "related_microbes": [
            "corynebacterium_glutamicum",
            "escherichia_coli",
            "aspergillus_niger",
            "saccharomyces_cerevisiae"
        ],
        "related_substrates": [
            "molasses",
            "glucose",
            "sucrose",
            "cane_sugar"
        ]
    }
}

# Extended microbe profiles with food context
MICROBE_FOOD_PROFILES = {
    "lactobacillus_plantarum": {
        "name": "lactobacillus_plantarum",
        "display_name": "Lactobacillus plantarum",
        "optimal_temp": 30.0,
        "optimal_ph": 5.5,
        "max_yield": 25.0,
        "description": "Versatile lactic acid bacteria found in fermented foods",
        "role": "Breaks proteins into peptides and amino acids, improves digestibility and bioavailability",
        "food_types": ["bread_grains", "legumes", "vegetables", "fermented_foods", "agro_waste"]
    },
    "lactobacillus_casei": {
        "name": "lactobacillus_casei",
        "display_name": "Lactobacillus casei",
        "optimal_temp": 30.0,
        "optimal_ph": 5.5,
        "max_yield": 22.0,
        "description": "Probiotic bacterium used in dairy fermentations",
        "role": "Enhances protein digestion, improves nutritional quality",
        "food_types": ["milk_products", "fermented_foods", "dairy_waste"]
    },
    "bacillus_subtilis": {
        "name": "bacillus_subtilis",
        "display_name": "Bacillus subtilis",
        "optimal_temp": 37.0,
        "optimal_ph": 7.0,
        "max_yield": 30.0,
        "description": "GRAS-status bacterium for food-grade protein production",
        "role": "Produces strong proteases, increases amino acid availability",
        "food_types": ["bread_grains", "legumes", "vegetables", "meat_fish", "oilseed_cakes"]
    },
    "bacillus_licheniformis": {
        "name": "bacillus_licheniformis",
        "display_name": "Bacillus licheniformis",
        "optimal_temp": 37.0,
        "optimal_ph": 7.0,
        "max_yield": 28.0,
        "description": "Industrial enzyme producer from agricultural residues",
        "role": "Hydrolyses complex proteins, used in industrial enzyme production",
        "food_types": ["bread_grains", "legumes", "oilseed_cakes", "agro_waste"]
    },
    "streptococcus_thermophilus": {
        "name": "streptococcus_thermophilus",
        "display_name": "Streptococcus thermophilus",
        "optimal_temp": 40.0,
        "optimal_ph": 6.5,
        "max_yield": 20.0,
        "description": "Thermophilic dairy fermentation bacterium",
        "role": "Partial protein breakdown, improves digestibility",
        "food_types": ["milk_products", "dairy_waste"]
    },
    "propionibacterium_freudenreichii": {
        "name": "propionibacterium_freudenreichii",
        "display_name": "Propionibacterium freudenreichii",
        "optimal_temp": 30.0,
        "optimal_ph": 6.5,
        "max_yield": 18.0,
        "description": "Swiss cheese bacterium producing vitamin B12",
        "role": "Enhances nutritional value, produces vitamin B12",
        "food_types": ["milk_products", "dairy_waste"]
    },
    "pseudomonas_fluorescens": {
        "name": "pseudomonas_fluorescens",
        "display_name": "Pseudomonas fluorescens",
        "optimal_temp": 25.0,
        "optimal_ph": 7.0,
        "max_yield": 15.0,
        "description": "Proteolytic bacterium for protein degradation studies",
        "role": "Strong proteolytic activity, used in protein degradation studies",
        "food_types": ["vegetables", "meat_fish"]
    },
    "lactobacillus_rhamnosus": {
        "name": "lactobacillus_rhamnosus",
        "display_name": "Lactobacillus rhamnosus",
        "optimal_temp": 30.0,
        "optimal_ph": 5.5,
        "max_yield": 20.0,
        "description": "Probiotic strain with bioactive peptide production",
        "role": "Improves protein digestibility, produces bioactive peptides",
        "food_types": ["milk_products", "fermented_foods", "dairy_waste"]
    },
    "lactobacillus_acidophilus": {
        "name": "lactobacillus_acidophilus",
        "display_name": "Lactobacillus acidophilus",
        "optimal_temp": 37.0,
        "optimal_ph": 5.5,
        "max_yield": 18.0,
        "description": "Common probiotic in yogurt and supplements",
        "role": "Enhances protein absorption, improves gut utilization of proteins",
        "food_types": ["milk_products", "dairy_waste", "fermented_foods"]
    },
    "bifidobacterium_bifidum": {
        "name": "bifidobacterium_bifidum",
        "display_name": "Bifidobacterium bifidum",
        "optimal_temp": 37.0,
        "optimal_ph": 6.0,
        "max_yield": 15.0,
        "description": "Gut-friendly bacterium in infant formulas",
        "role": "Improves protein digestion indirectly, enhances gut microbiota",
        "food_types": ["milk_products"]
    },
    "enterococcus_faecium": {
        "name": "enterococcus_faecium",
        "display_name": "Enterococcus faecium",
        "optimal_temp": 30.0,
        "optimal_ph": 6.5,
        "max_yield": 17.0,
        "description": "Ripening bacterium in dairy and meat products",
        "role": "Proteolytic activity, improves amino acid profile",
        "food_types": ["milk_products", "meat_fish"]
    },
    "micrococcus_luteus": {
        "name": "micrococcus_luteus",
        "display_name": "Micrococcus luteus",
        "optimal_temp": 30.0,
        "optimal_ph": 7.0,
        "max_yield": 12.0,
        "description": "Skin bacterium used in flavor development",
        "role": "Protein degradation, flavor development",
        "food_types": ["meat_fish"]
    },
    "clostridium_butyricum": {
        "name": "clostridium_butyricum",
        "display_name": "Clostridium butyricum",
        "optimal_temp": 30.0,
        "optimal_ph": 6.5,
        "max_yield": 14.0,
        "description": "Anaerobic bacterium from protein-rich organic matter",
        "role": "Protein breakdown under anaerobic conditions, produces beneficial metabolites",
        "food_types": ["agro_waste"]
    },
    "corynebacterium_glutamicum": {
        "name": "corynebacterium_glutamicum",
        "display_name": "Corynebacterium glutamicum",
        "optimal_temp": 30.0,
        "optimal_ph": 7.5,
        "max_yield": 35.0,
        "description": "Industrial amino acid production workhorse",
        "role": "Produces amino acids (glutamate, lysine), used in industrial protein enrichment",
        "food_types": ["legumes", "oilseed_cakes", "sugar_waste"]
    },
    "escherichia_coli": {
        "name": "escherichia_coli",
        "display_name": "Escherichia coli",
        "optimal_temp": 37.0,
        "optimal_ph": 7.0,
        "max_yield": 35.0,
        "description": "Fast-growing bacterium, standard host for recombinant proteins",
        "role": "Used in recombinant protein production, produces specific proteins",
        "food_types": ["legumes", "dairy_waste", "sugar_waste"]
    },
    "pediococcus_acidilactici": {
        "name": "pediococcus_acidilactici",
        "display_name": "Pediococcus acidilactici",
        "optimal_temp": 30.0,
        "optimal_ph": 5.5,
        "max_yield": 16.0,
        "description": "Fermentation bacterium for meat and cereal foods",
        "role": "Protein breakdown, improves texture and quality",
        "food_types": ["fermented_foods", "meat_fish"]
    },
    "saccharomyces_cerevisiae": {
        "name": "saccharomyces_cerevisiae",
        "display_name": "Saccharomyces cerevisiae",
        "optimal_temp": 30.0,
        "optimal_ph": 5.0,
        "max_yield": 45.0,
        "description": "Baker's yeast, widely used for protein production",
        "role": "Efficient carbon source utilization, high protein yield",
        "food_types": ["bread_grains", "sugar_waste", "agro_waste"]
    },
    "aspergillus_niger": {
        "name": "aspergillus_niger",
        "display_name": "Aspergillus niger",
        "optimal_temp": 30.0,
        "optimal_ph": 4.5,
        "max_yield": 40.0,
        "description": "Filamentous fungus for enzyme and organic acid production",
        "role": "Produces amylases and proteases, converts waste to protein",
        "food_types": ["bread_grains", "vegetables", "oilseed_cakes", "agro_waste", "sugar_waste"]
    },
    "pichia_pastoris": {
        "name": "pichia_pastoris",
        "display_name": "Pichia pastoris",
        "optimal_temp": 28.0,
        "optimal_ph": 5.5,
        "max_yield": 55.0,
        "description": "Methylotrophic yeast for secreted protein production",
        "role": "High protein secretion, excellent for heterologous protein expression",
        "food_types": ["sugar_waste", "agro_waste"]
    }
}

# Extended substrate profiles with food context
SUBSTRATE_FOOD_PROFILES = {
    "lactose": {"name": "lactose", "display_name": "Lactose", "energy": 16.5, "description": "Milk sugar, disaccharide from dairy", "food_types": ["milk_products", "dairy_waste"]},
    "milk_serum": {"name": "milk_serum", "display_name": "Milk Serum", "energy": 8.0, "description": "Liquid remaining after milk coagulation", "food_types": ["milk_products", "dairy_waste"]},
    "whey": {"name": "whey", "display_name": "Whey", "energy": 12.0, "description": "Liquid byproduct of cheese making", "food_types": ["milk_products", "dairy_waste"]},
    "casein": {"name": "casein", "display_name": "Casein", "energy": 15.0, "description": "Major milk protein", "food_types": ["milk_products", "dairy_waste"]},
    "skim_milk": {"name": "skim_milk", "display_name": "Skim Milk", "energy": 14.0, "description": "Dehydrated skimmed milk", "food_types": ["milk_products", "dairy_waste"]},
    "glucose": {"name": "glucose", "display_name": "Glucose", "energy": 15.6, "description": "Simple monosaccharide, most common carbon source", "food_types": ["bread_grains", "legumes", "vegetables", "fermented_foods", "sugar_waste", "agro_waste"]},
    "sucrose": {"name": "sucrose", "display_name": "Sucrose", "energy": 16.5, "description": "Disaccharide from sugarcane/beets", "food_types": ["bread_grains", "vegetables", "fermented_foods", "sugar_waste"]},
    "maltose": {"name": "maltose", "display_name": "Maltose", "energy": 15.8, "description": "Disaccharide from starch hydrolysis", "food_types": ["bread_grains"]},
    "starch": {"name": "starch", "display_name": "Starch", "energy": 17.0, "description": "Complex carbohydrate from grains", "food_types": ["bread_grains", "legumes"]},
    "wheat_bran": {"name": "wheat_bran", "display_name": "Wheat Bran", "energy": 8.0, "description": "Outer layer of wheat kernel", "food_types": ["bread_grains", "agro_waste"]},
    "rice_bran": {"name": "rice_bran", "display_name": "Rice Bran", "energy": 7.5, "description": "Outer layer of rice kernel", "food_types": ["bread_grains", "agro_waste"]},
    "soy_protein": {"name": "soy_protein", "display_name": "Soy Protein", "energy": 16.0, "description": "Extracted soy protein isolate", "food_types": ["legumes", "oilseed_cakes"]},
    "legume_extract": {"name": "legume_extract", "display_name": "Legume Extract", "energy": 14.0, "description": "Water-soluble extract from legumes", "food_types": ["legumes"]},
    "fructose": {"name": "fructose", "display_name": "Fructose", "energy": 15.6, "description": "Simple sugar from fruits", "food_types": ["vegetables", "sugar_waste"]},
    "pectin": {"name": "pectin", "display_name": "Pectin", "energy": 10.0, "description": "Polysaccharide from fruit cell walls", "food_types": ["vegetables"]},
    "cellulose": {"name": "cellulose", "display_name": "Cellulose", "energy": 6.0, "description": "Plant fiber, complex carbohydrate", "food_types": ["vegetables", "agro_waste"]},
    "peptone": {"name": "peptone", "display_name": "Peptone", "energy": 14.0, "description": "Enzymatic digest of proteins", "food_types": ["meat_fish"]},
    "yeast_extract": {"name": "yeast_extract", "display_name": "Yeast Extract", "energy": 18.0, "description": "Rich nitrogen source from yeast", "food_types": ["meat_fish", "fermented_foods"]},
    "meat_extract": {"name": "meat_extract", "display_name": "Meat Extract", "energy": 15.0, "description": "Concentrated meat solubles", "food_types": ["meat_fish"]},
    "fish_hydrolysate": {"name": "fish_hydrolysate", "display_name": "Fish Hydrolysate", "energy": 14.0, "description": "Enzymatically hydrolyzed fish material", "food_types": ["meat_fish"]},
    "vegetable_extract": {"name": "vegetable_extract", "display_name": "Vegetable Extract", "energy": 12.0, "description": "Water-soluble plant extracts", "food_types": ["vegetables", "fermented_foods"]},
    "salt_brine": {"name": "salt_brine", "display_name": "Salt Brine", "energy": 0.5, "description": "Salty water for fermentation", "food_types": ["fermented_foods"]},
    "groundnut_cake": {"name": "groundnut_cake", "display_name": "Groundnut Cake", "energy": 14.0, "description": "Byproduct of groundnut oil extraction", "food_types": ["oilseed_cakes"]},
    "sunflower_cake": {"name": "sunflower_cake", "display_name": "Sunflower Cake", "energy": 13.0, "description": "Byproduct of sunflower oil extraction", "food_types": ["oilseed_cakes"]},
    "soybean_meal": {"name": "soybean_meal", "display_name": "Soybean Meal", "energy": 15.0, "description": "Defatted soy flakes", "food_types": ["oilseed_cakes", "legumes"]},
    "cottonseed_meal": {"name": "cottonseed_meal", "display_name": "Cottonseed Meal", "energy": 13.5, "description": "Byproduct of cottonseed oil extraction", "food_types": ["oilseed_cakes"]},
    "corn_stover": {"name": "corn_stover", "display_name": "Corn Stover", "energy": 6.0, "description": "Corn plant residues after harvest", "food_types": ["agro_waste"]},
    "sugarcane_bagasse": {"name": "sugarcane_bagasse", "display_name": "Sugarcane Bagasse", "energy": 5.0, "description": "Fibrous residue after sugarcane crushing", "food_types": ["agro_waste", "sugar_waste"]},
    "molasses": {"name": "molasses", "display_name": "Molasses", "energy": 13.0, "description": "Byproduct of sugar refining", "food_types": ["agro_waste", "sugar_waste"]},
    "cane_sugar": {"name": "cane_sugar", "display_name": "Cane Sugar", "energy": 16.5, "description": "Raw sugar from sugarcane", "food_types": ["sugar_waste"]},
    "buttermilk": {"name": "buttermilk", "display_name": "Buttermilk", "energy": 10.0, "description": "Liquid remaining after churning butter", "food_types": ["dairy_waste"]},
    "glycerol": {"name": "glycerol", "display_name": "Glycerol", "energy": 17.6, "description": "Byproduct of biodiesel, economical carbon source", "food_types": ["sugar_waste"]},
    "methanol": {"name": "methanol", "display_name": "Methanol", "energy": 22.7, "description": "For methylotrophic yeasts like Pichia", "food_types": ["sugar_waste"]}
}


@router.get("/food-types", response_model=List[FoodTypeInfo])
async def list_food_types():
    """
    List all available food type categories with their related microbes and substrates.
    """
    food_types = []
    for key, data in FOOD_TYPE_DATA.items():
        food_types.append(FoodTypeInfo(
            name=data["name"],
            display_name=data["display_name"],
            description=data["description"],
            icon=data["icon"],
            related_microbes=data["related_microbes"],
            related_substrates=data["related_substrates"]
        ))
    return food_types


@router.get("/microbes/by-food/{food_type}", response_model=List[MicrobeWithFoodContext])
async def get_microbes_by_food(food_type: str):
    """
    Get microorganisms suitable for a specific food type.
    """
    if food_type not in FOOD_TYPE_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food type '{food_type}' not found"
        )
    
    related_microbes = FOOD_TYPE_DATA[food_type]["related_microbes"]
    microbes = []
    
    for microbe_name in related_microbes:
        if microbe_name in MICROBE_FOOD_PROFILES:
            profile = MICROBE_FOOD_PROFILES[microbe_name]
            microbes.append(MicrobeWithFoodContext(
                name=profile["name"],
                display_name=profile["display_name"],
                optimal_temp=profile["optimal_temp"],
                optimal_ph=profile["optimal_ph"],
                max_yield=profile["max_yield"],
                description=profile["description"],
                role=profile["role"],
                food_types=profile["food_types"]
            ))
        else:
            logger.warning(f"Microbe '{microbe_name}' referenced in food type '{food_type}' not found in MICROBE_FOOD_PROFILES")
    
    return microbes


@router.get("/substrates/by-food/{food_type}", response_model=List[SubstrateWithFoodContext])
async def get_substrates_by_food(food_type: str):
    """
    Get substrates suitable for a specific food type.
    """
    if food_type not in FOOD_TYPE_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food type '{food_type}' not found"
        )
    
    related_substrates = FOOD_TYPE_DATA[food_type]["related_substrates"]
    substrates = []
    
    for substrate_name in related_substrates:
        if substrate_name in SUBSTRATE_FOOD_PROFILES:
            profile = SUBSTRATE_FOOD_PROFILES[substrate_name]
            substrates.append(SubstrateWithFoodContext(
                name=profile["name"],
                display_name=profile["display_name"],
                energy=profile["energy"],
                description=profile["description"],
                food_types=profile["food_types"]
            ))
        else:
            logger.warning(f"Substrate '{substrate_name}' referenced in food type '{food_type}' not found in SUBSTRATE_FOOD_PROFILES")
    
    return substrates


# ── Food-category → Curated Protein + Organism suggestions ──
# Maps food categories to scientifically relevant proteins based on KEGG/UniProt knowledge.
PROTEIN_SUGGESTIONS = {
    "milk_products": [
        {"protein_name": "Beta-lactoglobulin", "organism": "Bos taurus", "description": "Major whey protein in cow milk, key allergen and functional protein", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Casein", "organism": "Bos taurus", "description": "Primary milk protein family (αS1, αS2, β, κ), forms micelles", "kegg_pathway": "Amino acid metabolism"},
        {"protein_name": "Alpha-lactalbumin", "organism": "Bos taurus", "description": "Whey protein involved in lactose synthesis", "kegg_pathway": "Galactose metabolism"},
        {"protein_name": "Lactoferrin", "organism": "Bos taurus", "description": "Iron-binding glycoprotein with antimicrobial properties", "kegg_pathway": "Mineral absorption"},
    ],
    "dairy_waste": [
        {"protein_name": "Beta-lactoglobulin", "organism": "Bos taurus", "description": "Major whey protein recovered from dairy waste streams", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Casein", "organism": "Bos taurus", "description": "Recovered from acid whey and cheese processing waste", "kegg_pathway": "Amino acid metabolism"},
        {"protein_name": "Bovine serum albumin", "organism": "Bos taurus", "description": "Serum protein found in dairy waste whey fractions", "kegg_pathway": "Protein processing"},
    ],
    "bread_grains": [
        {"protein_name": "Glutenin", "organism": "Triticum aestivum", "description": "High molecular weight wheat storage protein", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Gliadin", "organism": "Triticum aestivum", "description": "Prolamin storage protein in wheat endosperm", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Amylase", "organism": "Aspergillus oryzae", "description": "Starch-degrading enzyme used in grain processing", "kegg_pathway": "Starch and sucrose metabolism"},
        {"protein_name": "Oryzenin", "organism": "Oryza sativa", "description": "Major storage protein in rice grain", "kegg_pathway": "Amino acid biosynthesis"},
    ],
    "legumes": [
        {"protein_name": "Glycinin", "organism": "Glycine max", "description": "11S globulin, major soy storage protein", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Leghemoglobin", "organism": "Glycine max", "description": "Heme protein for meat alternatives (Impossible Foods-style)", "kegg_pathway": "Porphyrin metabolism"},
        {"protein_name": "Legumin", "organism": "Pisum sativum", "description": "Major pea storage protein, excellent emulsifier", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Vicilin", "organism": "Pisum sativum", "description": "7S globulin from pea, good gelation properties", "kegg_pathway": "Amino acid biosynthesis"},
    ],
    "vegetables": [
        {"protein_name": "RuBisCO", "organism": "Spinacia oleracea", "description": "Most abundant protein on Earth, extracted from leaves", "kegg_pathway": "Carbon fixation"},
        {"protein_name": "Patatin", "organism": "Solanum tuberosum", "description": "Storage protein from potato tuber", "kegg_pathway": "Lipid metabolism"},
        {"protein_name": "Thaumatin", "organism": "Thaumatococcus daniellii", "description": "Sweet-tasting protein, natural sweetener", "kegg_pathway": "Amino acid biosynthesis"},
    ],
    "meat_fish": [
        {"protein_name": "Myoglobin", "organism": "Bos taurus", "description": "Oxygen-binding heme protein giving meat its red color", "kegg_pathway": "Porphyrin metabolism"},
        {"protein_name": "Collagen", "organism": "Bos taurus", "description": "Structural protein for texture in meat alternatives", "kegg_pathway": "Protein digestion and absorption"},
        {"protein_name": "Tropomyosin", "organism": "Penaeus monodon", "description": "Major shellfish allergen and muscle protein", "kegg_pathway": "Cardiac muscle contraction"},
        {"protein_name": "Ovalbumin", "organism": "Gallus gallus", "description": "Major egg white protein, excellent gelling agent", "kegg_pathway": "Amino acid metabolism"},
    ],
    "fermented_foods": [
        {"protein_name": "Subtilisin", "organism": "Bacillus subtilis", "description": "Serine protease for protein hydrolysis in fermentation", "kegg_pathway": "Protein processing"},
        {"protein_name": "Alpha-amylase", "organism": "Bacillus amyloliquefaciens", "description": "Starch-degrading enzyme for carbohydrate fermentation", "kegg_pathway": "Starch and sucrose metabolism"},
        {"protein_name": "Nattokinase", "organism": "Bacillus subtilis", "description": "Fibrinolytic enzyme from natto fermentation", "kegg_pathway": "Complement and coagulation cascades"},
        {"protein_name": "Lipase", "organism": "Aspergillus niger", "description": "Fat-splitting enzyme in fermented food production", "kegg_pathway": "Glycerolipid metabolism"},
    ],
    "oilseed_cakes": [
        {"protein_name": "Cruciferin", "organism": "Brassica napus", "description": "12S globulin from rapeseed/canola", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Glycinin", "organism": "Glycine max", "description": "11S globulin from soybean meal", "kegg_pathway": "Amino acid biosynthesis"},
        {"protein_name": "Arachin", "organism": "Arachis hypogaea", "description": "Major storage protein from groundnut", "kegg_pathway": "Amino acid biosynthesis"},
    ],
    "sugar_waste": [
        {"protein_name": "Invertase", "organism": "Saccharomyces cerevisiae", "description": "Sucrose-hydrolyzing enzyme from yeast", "kegg_pathway": "Starch and sucrose metabolism"},
        {"protein_name": "Levanase", "organism": "Bacillus subtilis", "description": "Levan-degrading enzyme for fructan processing", "kegg_pathway": "Starch and sucrose metabolism"},
    ],
    "agro_waste": [
        {"protein_name": "Cellulase", "organism": "Trichoderma reesei", "description": "Cellulose-degrading enzyme for biomass conversion", "kegg_pathway": "Starch and sucrose metabolism"},
        {"protein_name": "Xylanase", "organism": "Aspergillus niger", "description": "Hemicellulose-degrading enzyme for lignocellulosic waste", "kegg_pathway": "Pentose and glucuronate interconversions"},
        {"protein_name": "Laccase", "organism": "Trametes versicolor", "description": "Lignin-degrading enzyme for agricultural waste processing", "kegg_pathway": "Phenylpropanoid biosynthesis"},
    ],
}


@router.get("/protein-suggestions/{food_type}")
async def get_protein_suggestions(food_type: str):
    """
    Return scientifically curated protein + organism suggestions for a food category.
    Leverages KEGG pathway knowledge and UniProt organism mappings.
    """
    suggestions = PROTEIN_SUGGESTIONS.get(food_type, [])
    if not suggestions:
        # Fallback: return general functional proteins
        suggestions = [
            {"protein_name": "Ovalbumin", "organism": "Gallus gallus", "description": "Versatile egg white protein", "kegg_pathway": "Amino acid metabolism"},
            {"protein_name": "Casein", "organism": "Bos taurus", "description": "Major milk protein", "kegg_pathway": "Amino acid metabolism"},
        ]
    return suggestions

@router.get("/microbes", response_model=List[MicrobeInfo])
async def list_microbes():
    """
    List all supported microbe types with their profiles.
    """
    microbes = []
    descriptions = {
        "saccharomyces_cerevisiae": "Baker's yeast, widely used for protein production and fermentation",
        "escherichia_coli": "Fast-growing bacterium, standard host for recombinant proteins",
        "pichia_pastoris": "Methylotrophic yeast, excellent for secreted protein production",
        "aspergillus_niger": "Filamentous fungus, used for enzyme and organic acid production",
        "bacillus_subtilis": "Gram-positive bacterium, GRAS status for food applications"
    }
    
    for name, profile in simulator.MICROBE_PROFILES.items():
        microbes.append(MicrobeInfo(
            name=name,
            display_name=name.replace("_", " ").title(),
            optimal_temp=profile["optimal_temp"],
            optimal_ph=profile["optimal_ph"],
            max_yield=profile["max_yield"],
            description=descriptions.get(name, "")
        ))
    
    return microbes


@router.get("/substrates", response_model=List[SubstrateInfo])
async def list_substrates():
    """
    List all supported substrates with their properties.
    """
    substrates = []
    descriptions = {
        "glucose": "Simple monosaccharide, most common carbon source",
        "sucrose": "Disaccharide from sugarcane/beets, cost-effective",
        "maltose": "Disaccharide from starch hydrolysis",
        "glycerol": "Byproduct of biodiesel, economical carbon source",
        "methanol": "For methylotrophic yeasts like Pichia",
        "lactose": "Milk sugar, used for specific inducible systems",
        "starch": "Complex carbohydrate, requires hydrolysis"
    }
    
    for name, profile in simulator.SUBSTRATE_PROFILES.items():
        substrates.append(SubstrateInfo(
            name=name,
            display_name=name.title(),
            energy=profile["energy"],
            description=descriptions.get(name, "")
        ))
    
    return substrates


@router.get("/microbes/with-food-context", response_model=List[MicrobeWithFoodContext])
async def list_microbes_with_context():
    """
    List all microorganisms with their food type context.
    """
    microbes = []
    for name, profile in MICROBE_FOOD_PROFILES.items():
        microbes.append(MicrobeWithFoodContext(
            name=profile["name"],
            display_name=profile["display_name"],
            optimal_temp=profile["optimal_temp"],
            optimal_ph=profile["optimal_ph"],
            max_yield=profile["max_yield"],
            description=profile["description"],
            role=profile["role"],
            food_types=profile["food_types"]
        ))
    return microbes


@router.get("/substrates/with-food-context", response_model=List[SubstrateWithFoodContext])
async def list_substrates_with_context():
    """
    List all substrates with their food type context.
    """
    substrates = []
    for name, profile in SUBSTRATE_FOOD_PROFILES.items():
        substrates.append(SubstrateWithFoodContext(
            name=profile["name"],
            display_name=profile["display_name"],
            energy=profile["energy"],
            description=profile["description"],
            food_types=profile["food_types"]
        ))
    return substrates


@router.post("/run", response_model=ExperimentWithResult, status_code=status.HTTP_201_CREATED)
async def run_experiment(
    experiment_data: ExperimentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run a new fermentation simulation experiment.
    
    Creates an experiment record and runs the ML simulation to predict outcomes.
    """
    # Create experiment record
    experiment = Experiment(
        user_id=current_user.id,
        name=experiment_data.name,
        microbe_type=experiment_data.microbe_type,
        substrate=experiment_data.substrate,
        temperature=experiment_data.temperature,
        ph=experiment_data.ph,
        duration=experiment_data.duration,
        oxygen_level=experiment_data.oxygen_level,
        agitation_speed=experiment_data.agitation_speed,
        status="running"
    )
    
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    
    # Optional Real-Time Data Fetching
    realtime_substrate_mw = None
    realtime_protein_length = None
    realtime_plddt = None
    pdb_string_for_viewer = ""
    recommendations_list = []
    
    if experiment_data.use_realtime_data and experiment_data.protein_name:
        try:
            logger.info(f"Fetching real-time API data for {experiment_data.substrate} and {experiment_data.protein_name}")
            pipeline_res = run_fermentation_pipeline(
                substrate_name=experiment_data.substrate,
                protein_name=experiment_data.protein_name,
                organism=experiment_data.organism or "Gallus gallus",
                predict_structure=experiment_data.predict_structure
            )
            
            # Extract attributes to adjust ML
            # Keys match run_fermentation_pipeline() output: substrate, protein, structure
            sub_data = pipeline_res.get("substrate", {})
            if sub_data and "error" not in sub_data:
                mw_raw = sub_data.get("molecular_weight")
                try:
                    realtime_substrate_mw = float(mw_raw) if mw_raw is not None else None
                except (ValueError, TypeError):
                    realtime_substrate_mw = None
                formula = sub_data.get("formula", "")
                recommendations_list.append(
                    f"📦 PubChem: {experiment_data.substrate} → MW: {realtime_substrate_mw} g/mol, Formula: {formula}"
                )

            prot_data = pipeline_res.get("protein", {})
            if prot_data and "error" not in prot_data:
                len_raw = prot_data.get("sequence_length")
                try:
                    realtime_protein_length = int(len_raw) if len_raw is not None else None
                except (ValueError, TypeError):
                    realtime_protein_length = None
                accession = prot_data.get("accession", "")
                seq_preview = prot_data.get("sequence_preview", "")
                recommendations_list.append(
                    f"🧬 UniProt: {experiment_data.protein_name} ({accession}) → {realtime_protein_length} amino acids. Seq: {seq_preview}"
                )

            struct_data = pipeline_res.get("structure", {})
            pdb_string_for_viewer = ""
            if struct_data and "error" not in struct_data and not struct_data.get("skipped"):
                plddt_raw = struct_data.get("mean_plddt")
                try:
                    realtime_plddt = float(plddt_raw) if plddt_raw is not None else None
                except (ValueError, TypeError):
                    realtime_plddt = None
                confidence_interp = struct_data.get("confidence_interpretation", "")
                if realtime_plddt is not None:
                    recommendations_list.append(
                        f"🔬 ESMFold: 3D structure confidence pLDDT = {realtime_plddt:.1f}/100 — {confidence_interp}"
                    )
                else:
                    recommendations_list.append(
                        f"⚠️ ESMFold: Structure predicted but pLDDT could not be parsed"
                    )
                pdb_string_for_viewer = struct_data.get("pdb_data", "")
                if not pdb_string_for_viewer:
                    recommendations_list.append(
                        f"⚠️ ESMFold: PDB data empty ({struct_data.get('pdb_length_chars', 0)} chars)"
                    )
                    logger.warning(f"ESMFold returned empty PDB data: {struct_data}")
            elif struct_data.get("skipped"):
                logger.info(f"Structure prediction skipped: {struct_data.get('reason')}")
            else:
                error_msg = struct_data.get("error", "Unknown error")
                recommendations_list.append(
                    f"❌ ESMFold failed: {error_msg}"
                )
                logger.error(f"ESMFold structure prediction failed: {error_msg}")

            # fermentation_insights is a list of strings
            insights_list = pipeline_res.get("fermentation_insights", [])
            if isinstance(insights_list, list):
                for insight in insights_list:
                    # Use API-specific emoji if the insight mentions a source
                    if insight.startswith("KEGG"):
                        recommendations_list.append(f"🗺️ {insight}")
                    elif insight.startswith("BioNumbers"):
                        recommendations_list.append(f"📊 {insight}")
                    else:
                        recommendations_list.append(f"💡 {insight}")

            # KEGG pathway data
            kegg_data = pipeline_res.get("kegg", {})
            if kegg_data and "error" not in kegg_data:
                pathways = kegg_data.get("pathways", [])
                if pathways:
                    pathway_names = [p.get("name", "Unknown") for p in pathways[:3]]
                    recommendations_list.append(
                        f"🗺️ KEGG Metabolic Pathways: {', '.join(pathway_names)}"
                    )
                cpd = kegg_data.get("compound", {})
                if cpd.get("kegg_id"):
                    recommendations_list.append(
                        f"🗺️ KEGG Compound {cpd['kegg_id']}: {cpd.get('formula', '')} (MW {cpd.get('mol_weight', '')} g/mol)"
                    )

            # BioNumbers — microbe-specific published growth data
            from app.realtime_pipeline import bionumbers_get_organism
            bio_data = bionumbers_get_organism(experiment_data.microbe_type)
            if "error" not in bio_data:
                recommendations_list.append(
                    f"📊 BioNumbers: {experiment_data.microbe_type.replace('_', ' ').title()} → "
                    f"Growth rate: {bio_data.get('growth_rate')} /h, "
                    f"Doubling time: {bio_data.get('doubling_time_min')} min, "
                    f"Max yield: {bio_data.get('max_yield_g_per_g')} g/g "
                    f"(BNID: {bio_data.get('bnid')})"
                )
                # Use BioNumbers optimal conditions to enhance recommendations
                bio_optimal_temp = bio_data.get("optimal_temp")
                bio_optimal_ph = bio_data.get("optimal_ph")
                if bio_optimal_temp and bio_optimal_ph:
                    temp_diff = abs(experiment_data.temperature - bio_optimal_temp)
                    ph_diff = abs(experiment_data.ph - bio_optimal_ph)
                    if temp_diff > 3 or ph_diff > 1:
                        recommendations_list.append(
                            f"⚠️ BioNumbers suggests optimal: {bio_optimal_temp}°C, pH {bio_optimal_ph} "
                            f"(Ref: {bio_data.get('reference', '')}). Your settings differ — consider adjusting."
                        )
                
        except Exception as e:
            logger.error(f"Real-time pipeline failed but continuing: {e}")
            recommendations_list.append("Real-time data fetch failed; fell back to baseline models.")
            
    # Run simulation
    try:
        params = FermentationParams(
            microbe_type=experiment_data.microbe_type,
            substrate=experiment_data.substrate,
            temperature=experiment_data.temperature,
            ph=experiment_data.ph,
            duration=experiment_data.duration,
            oxygen_level=experiment_data.oxygen_level,
            agitation_speed=experiment_data.agitation_speed,
            bioreactor_volume=experiment_data.bioreactor_volume,
            realtime_substrate_mw=realtime_substrate_mw,
            realtime_protein_length=realtime_protein_length,
            realtime_plddt=realtime_plddt
        )
        sim_result = simulator.simulate(params)
        
        # Build recommendations text (with optional PDB data embedded for 3D viewer)
        recs_text = " ".join(recommendations_list) if recommendations_list else ""
        if pdb_string_for_viewer:
            recs_text += f" __PDB_START__{pdb_string_for_viewer}__PDB_END__"
        
        # Embed Machine Learning Models executed
        if hasattr(sim_result, 'executed_models') and sim_result.executed_models:
            import json
            models_json = json.dumps(sim_result.executed_models)
            recs_text += f" __MODELS_START__{models_json}__MODELS_END__"

        # Create result record
        result = Result(
            experiment_id=experiment.id,
            predicted_yield=sim_result.predicted_yield,
            energy_usage=sim_result.energy_usage,
            co2_footprint=sim_result.co2_footprint,
            protein_score=sim_result.protein_score,
            purity=sim_result.purity,
            efficiency=sim_result.efficiency,
            sustainability_score=sim_result.sustainability_score,
            explanation=None,  # Will be filled by AI explainer
            recommendations=recs_text or None
        )
        
        db.add(result)
        experiment.status = "completed"
        await db.commit()
        await db.refresh(result)
        
    except Exception as e:
        experiment.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )
    
    return ExperimentWithResult(
        experiment=ExperimentResponse.model_validate(experiment),
        result=ResultResponse.model_validate(result)
    )


@router.get("/{experiment_id}", response_model=ExperimentWithResult)
async def get_experiment(
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific experiment by ID.
    """
    result = await db.execute(
        select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.user_id == current_user.id
        )
    )
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # Get result if exists
    result_query = await db.execute(
        select(Result).where(Result.experiment_id == experiment_id)
    )
    exp_result = result_query.scalar_one_or_none()
    
    return ExperimentWithResult(
        experiment=ExperimentResponse.model_validate(experiment),
        result=ResultResponse.model_validate(exp_result) if exp_result else None
    )


@router.get("/", response_model=ExperimentListResponse)
async def list_experiments(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all experiments for the current user with pagination.
    """
    # Count total
    count_result = await db.execute(
        select(func.count(Experiment.id)).where(Experiment.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    # Get paginated experiments
    offset = (page - 1) * per_page
    experiments_result = await db.execute(
        select(Experiment)
        .where(Experiment.user_id == current_user.id)
        .order_by(Experiment.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    experiments = experiments_result.scalars().all()
    
    # Get results for each experiment
    experiment_list = []
    for exp in experiments:
        result_query = await db.execute(
            select(Result).where(Result.experiment_id == exp.id)
        )
        exp_result = result_query.scalar_one_or_none()
        
        experiment_list.append(ExperimentWithResult(
            experiment=ExperimentResponse.model_validate(exp),
            result=ResultResponse.model_validate(exp_result) if exp_result else None
        ))
    
    return ExperimentListResponse(
        experiments=experiment_list,
        total=total,
        page=page,
        per_page=per_page
    )


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an experiment and its results.
    """
    result = await db.execute(
        select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.user_id == current_user.id
        )
    )
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    await db.delete(experiment)
    await db.commit()
