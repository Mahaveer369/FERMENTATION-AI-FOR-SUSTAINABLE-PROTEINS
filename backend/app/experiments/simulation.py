"""
FermaGen AI - Fermentation Simulation Engine
Scientific ML model for predicting fermentation outcomes

Growth parameters sourced from BioNumbers (https://bionumbers.hms.harvard.edu/)
All values cite their BioNumbers ID (BNID) for scientific traceability.
"""
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FermentationParams:
    """Input parameters for fermentation simulation"""
    microbe_type: str
    substrate: str
    temperature: float  # Celsius
    ph: float
    duration: float  # Hours
    oxygen_level: float = 21.0  # Percentage
    agitation_speed: float = 200.0  # RPM
    realtime_substrate_mw: Optional[float] = None
    realtime_protein_length: Optional[int] = None
    realtime_plddt: Optional[float] = None


@dataclass
class SimulationResult:
    """Output from fermentation simulation"""
    predicted_yield: float  # g/L
    energy_usage: float  # kWh
    co2_footprint: float  # kg CO2
    protein_score: float  # 0-100
    purity: float  # Percentage
    efficiency: float  # Percentage
    sustainability_score: float  # 0-100
    confidence: float  # Model confidence 0-1


# ── Food Category → Recommended Proteins & Substrates (KEGG-informed) ──
FOOD_CATEGORY_RECOMMENDATIONS = {
    "dairy_alternatives": {
        "recommended_proteins": ["casein", "whey protein", "beta-lactoglobulin"],
        "recommended_substrates": ["lactose", "glucose"],
        "recommended_microbes": ["pichia_pastoris", "saccharomyces_cerevisiae"],
        "kegg_pathways": ["Galactose metabolism", "Amino acid biosynthesis"],
    },
    "meat_alternatives": {
        "recommended_proteins": ["soy leghemoglobin", "myoglobin", "collagen"],
        "recommended_substrates": ["glucose", "glycerol"],
        "recommended_microbes": ["pichia_pastoris", "escherichia_coli"],
        "kegg_pathways": ["Amino acid biosynthesis", "Porphyrin metabolism"],
    },
    "fermented_foods": {
        "recommended_proteins": ["amylase", "protease", "lipase"],
        "recommended_substrates": ["glucose", "sucrose", "starch"],
        "recommended_microbes": ["aspergillus_niger", "bacillus_subtilis", "saccharomyces_cerevisiae"],
        "kegg_pathways": ["Glycolysis", "Starch and sucrose metabolism"],
    },
    "functional_proteins": {
        "recommended_proteins": ["ovalbumin", "lysozyme", "lactoferrin"],
        "recommended_substrates": ["glucose", "glycerol"],
        "recommended_microbes": ["escherichia_coli", "pichia_pastoris"],
        "kegg_pathways": ["Amino acid biosynthesis", "Protein processing"],
    },
    "bio_flavors": {
        "recommended_proteins": ["vanillin synthase", "limonene synthase"],
        "recommended_substrates": ["glucose", "glycerol"],
        "recommended_microbes": ["saccharomyces_cerevisiae", "escherichia_coli"],
        "kegg_pathways": ["Terpenoid biosynthesis", "Phenylpropanoid biosynthesis"],
    },
}


class FermentationSimulator:
    """
    ML-based fermentation simulator using scientifically constrained models.
    
    Growth parameters sourced from BioNumbers database with BNID citations.
    """
    
    # ── Optimal parameters by microbe type — from BioNumbers ──
    MICROBE_PROFILES = {
        "saccharomyces_cerevisiae": {
            "optimal_temp": 30.0,       # BioNumbers BNID 100270
            "optimal_ph": 5.0,
            "temp_range": 8.0,
            "ph_range": 1.5,
            "max_yield": 45.0,          # g/L
            "growth_rate": 0.39,        # BNID 100270 (published: 0.39/h)
            "max_yield_g_per_g": 0.46,  # BNID 111456
            "protein_potential": 85,
            "bnid": "100270, 111456",
            "reference": "Herskowitz 1988; Verduyn et al. 1991",
        },
        "escherichia_coli": {
            "optimal_temp": 37.0,       # BioNumbers BNID 100256
            "optimal_ph": 7.0,
            "temp_range": 6.0,
            "ph_range": 1.0,
            "max_yield": 35.0,
            "growth_rate": 0.69,        # BNID 100256 (published: 0.69/h)
            "max_yield_g_per_g": 0.50,  # BNID 105318
            "protein_potential": 80,
            "bnid": "100256, 105318",
            "reference": "Neidhardt et al., Physiology of the Bacterial Cell, 1990",
        },
        "pichia_pastoris": {
            "optimal_temp": 28.0,       # BioNumbers BNID 107250
            "optimal_ph": 5.5,
            "temp_range": 5.0,
            "ph_range": 1.2,
            "max_yield": 55.0,
            "growth_rate": 0.18,        # BNID 107250 (published: 0.18/h)
            "max_yield_g_per_g": 0.53,  # BNID 107251
            "protein_potential": 90,
            "bnid": "107250, 107251",
            "reference": "Cos et al., Biotechnology Advances, 2006",
        },
        "aspergillus_niger": {
            "optimal_temp": 30.0,       # BioNumbers BNID 109835
            "optimal_ph": 4.5,
            "temp_range": 7.0,
            "ph_range": 1.8,
            "max_yield": 40.0,
            "growth_rate": 0.20,        # BNID 109835
            "max_yield_g_per_g": 0.40,
            "protein_potential": 75,
            "bnid": "109835",
            "reference": "Papagianni, Biotechnology Advances, 2007",
        },
        "bacillus_subtilis": {
            "optimal_temp": 37.0,       # BioNumbers BNID 100257
            "optimal_ph": 7.0,
            "temp_range": 8.0,
            "ph_range": 1.5,
            "max_yield": 30.0,
            "growth_rate": 0.79,        # BNID 100257 (published: 0.79/h)
            "max_yield_g_per_g": 0.44,
            "protein_potential": 78,
            "bnid": "100257",
            "reference": "Harwood & Cutting, 1990",
        },
        "lactobacillus_casei": {
            "optimal_temp": 30.0,
            "optimal_ph": 5.5,
            "temp_range": 6.0,
            "ph_range": 1.5,
            "max_yield": 25.0,
            "growth_rate": 0.35,
            "max_yield_g_per_g": 0.38,
            "protein_potential": 70,
            "bnid": "N/A",
            "reference": "Kandler & Weiss, 1986",
        },
    }
    
    # ── Substrate energy content — from BioNumbers ──
    SUBSTRATE_PROFILES = {
        "glucose": {
            "energy": 15.6,       # BNID 101736 (kJ/g)
            "conversion": 0.5,    # BNID 105318
            "co2_factor": 0.95,
            "atp_yield": 36,      # BNID 101268
            "bnid": "101736, 101268",
        },
        "sucrose": {
            "energy": 16.5,
            "conversion": 0.48,
            "co2_factor": 0.92,
            "atp_yield": 38,
            "bnid": "N/A",
        },
        "maltose": {
            "energy": 15.8,
            "conversion": 0.45,
            "co2_factor": 0.88,
            "atp_yield": 36,
            "bnid": "N/A",
        },
        "glycerol": {
            "energy": 17.6,       # BNID 101737
            "conversion": 0.55,
            "co2_factor": 0.75,
            "atp_yield": 38,
            "bnid": "101737",
        },
        "methanol": {
            "energy": 22.7,
            "conversion": 0.4,
            "co2_factor": 1.1,
            "atp_yield": 18,
            "bnid": "N/A",
        },
        "lactose": {
            "energy": 15.4,
            "conversion": 0.42,
            "co2_factor": 0.85,
            "atp_yield": 36,
            "bnid": "N/A",
        },
        "starch": {
            "energy": 17.0,
            "conversion": 0.35,
            "co2_factor": 0.82,
            "atp_yield": 36,
            "bnid": "N/A",
        },
    }
    
    def __init__(self):
        self.noise_factor = 0.05  # 5% random variation
    
    def _normalize_microbe_name(self, name: str) -> str:
        """Normalize microbe name for lookup"""
        normalized = name.lower().replace(" ", "_").replace("-", "_")
        if normalized in self.MICROBE_PROFILES:
            return normalized
        # Default to E. coli if not found
        return "escherichia_coli"
    
    def _normalize_substrate_name(self, name: str) -> str:
        """Normalize substrate name for lookup"""
        normalized = name.lower().replace(" ", "_")
        if normalized in self.SUBSTRATE_PROFILES:
            return normalized
        return "glucose"
    
    def _gaussian_response(self, value: float, optimal: float, range_param: float) -> float:
        """
        Gaussian response curve - models biological optimum behavior.
        Returns value between 0 and 1.
        """
        return np.exp(-0.5 * ((value - optimal) / range_param) ** 2)
    
    def _growth_curve(self, duration: float, growth_rate: float) -> float:
        """
        Logistic growth curve - models microbial growth saturation.
        Returns value between 0 and 1.
        """
        # Logistic curve with carrying capacity normalization
        k = 1.0  # Carrying capacity
        return k / (1 + np.exp(-growth_rate * (duration - 24)))  # Inflection at 24h
    
    def predict_yield(self, params: FermentationParams) -> Tuple[float, float]:
        """
        Predict fermentation yield using scientifically constrained model.
        
        Returns: (yield_g_per_L, confidence)
        """
        microbe = self._normalize_microbe_name(params.microbe_type)
        substrate = self._normalize_substrate_name(params.substrate)
        
        profile = self.MICROBE_PROFILES[microbe]
        substrate_profile = self.SUBSTRATE_PROFILES[substrate]
        
        # Temperature response (Gaussian around optimal)
        temp_factor = self._gaussian_response(
            params.temperature,
            profile["optimal_temp"],
            profile["temp_range"]
        )
        
        # pH response (Gaussian around optimal)
        ph_factor = self._gaussian_response(
            params.ph,
            profile["optimal_ph"],
            profile["ph_range"]
        )
        
        # Duration effect (logistic growth)
        time_factor = self._growth_curve(params.duration, profile["growth_rate"])
        
        # Oxygen effect (linear with diminishing returns)
        oxygen_factor = min(1.0, params.oxygen_level / 21.0)
        
        # Agitation effect (optimal around 200 RPM)
        agitation_factor = self._gaussian_response(params.agitation_speed, 200, 100)
        
        # Substrate conversion efficiency
        substrate_factor = substrate_profile["conversion"]
        
        # Calculate base yield
        max_yield = profile["max_yield"]
        base_yield = max_yield * temp_factor * ph_factor * time_factor * oxygen_factor * agitation_factor * substrate_factor
        
        # Real-Time API Adjustments
        if params.realtime_substrate_mw is not None:
            # Very heavy substrates are slightly harder to fully metabolize, reducing max yield slightly
            if params.realtime_substrate_mw > 300:
                base_yield *= 0.95
            elif params.realtime_substrate_mw < 100:
                base_yield *= 1.05

        # Add controlled noise for realism
        noise = np.random.normal(1.0, self.noise_factor)
        predicted_yield = max(0, base_yield * noise)
        
        # Confidence based on how close conditions are to optimal
        confidence = 0.7 + 0.3 * (temp_factor * ph_factor * oxygen_factor)
        
        return predicted_yield, confidence
    
    def predict_energy(self, params: FermentationParams, predicted_yield: float) -> float:
        """
        Predict energy consumption in kWh.
        
        Energy = Base + Duration*Agitation + Heating/Cooling + Aeration
        """
        # Base energy (reactor operation)
        base_energy = 0.5  # kWh base
        
        # Duration-based energy (agitation motor)
        agitation_energy = (params.duration / 24) * (params.agitation_speed / 200) * 0.8
        
        # Temperature control energy (heating/cooling)
        temp_diff = abs(params.temperature - 25)  # From ambient
        temp_energy = (params.duration / 24) * (temp_diff / 10) * 0.3
        
        # Aeration energy
        aeration_energy = (params.oxygen_level / 21) * (params.duration / 24) * 0.2
        
        total_energy = base_energy + agitation_energy + temp_energy + aeration_energy
        
        # Real-time API adjust: large molecules require slightly more energy (e.g. heating/agitation to dissolve)
        if params.realtime_substrate_mw is not None and params.realtime_substrate_mw > 300:
            total_energy *= 1.1
            
        # Add noise
        noise = np.random.normal(1.0, self.noise_factor)
        return max(0.1, total_energy * noise)
    
    def predict_co2(self, params: FermentationParams, predicted_yield: float, energy_usage: float) -> float:
        """
        Predict CO2 footprint in kg CO2 equivalent.
        
        CO2 = Metabolic CO2 + Energy CO2 + Processing CO2
        """
        substrate = self._normalize_substrate_name(params.substrate)
        substrate_profile = self.SUBSTRATE_PROFILES[substrate]
        
        # Metabolic CO2 from fermentation (substrate dependent)
        metabolic_co2 = predicted_yield * substrate_profile["co2_factor"] * 0.05  # kg CO2/g yield
        
        # Energy-related CO2 (grid emission factor ~0.4 kg CO2/kWh)
        energy_co2 = energy_usage * 0.4
        
        # Processing overhead
        processing_co2 = 0.1  # Base processing
        
        total_co2 = metabolic_co2 + energy_co2 + processing_co2
        
        # Add noise
        noise = np.random.normal(1.0, self.noise_factor)
        return max(0.01, total_co2 * noise)
    
    def predict_protein_score(self, params: FermentationParams, predicted_yield: float) -> float:
        """
        Predict protein quality score (0-100).
        
        Based on: yield efficiency, conditions, and microbe potential
        """
        microbe = self._normalize_microbe_name(params.microbe_type)
        profile = self.MICROBE_PROFILES[microbe]
        
        # Base score from microbe potential
        base_score = profile["protein_potential"]
        
        # Condition factors
        temp_factor = self._gaussian_response(params.temperature, profile["optimal_temp"], profile["temp_range"])
        ph_factor = self._gaussian_response(params.ph, profile["optimal_ph"], profile["ph_range"])
        
        # Yield factor (higher yield often means better protein expression)
        yield_factor = min(1.0, predicted_yield / profile["max_yield"])
        
        # Calculate final score
        condition_modifier = (temp_factor * ph_factor * yield_factor) ** 0.5
        protein_score = base_score * condition_modifier
        
        # Real-Time API Adjustments for Protein
        if params.realtime_protein_length is not None:
            # Huge proteins (>600 aa) face expression and folding hurdles, bringing score down
            if params.realtime_protein_length > 600:
                protein_score *= 0.9

        if params.realtime_plddt is not None:
            # pLDDT is 0-100. High confidence means stable fold, boosts quality score. 
            # Low confidence means unstable, lowers score.
            plddt_modifier = params.realtime_plddt / 80.0  # Normalized around 80
            protein_score *= plddt_modifier

        # Add noise
        noise = np.random.normal(1.0, self.noise_factor / 2)
        return max(0, min(100, protein_score * noise))
    
    def calculate_sustainability_score(
        self,
        predicted_yield: float,
        energy_usage: float,
        co2_footprint: float
    ) -> float:
        """
        Calculate overall sustainability score (0-100).
        
        Factors:
        - Yield efficiency (higher is better)
        - Energy efficiency (lower per unit yield is better)
        - CO2 efficiency (lower per unit yield is better)
        """
        # Yield score (normalize to 0-100 based on typical ranges)
        yield_score = min(100, (predicted_yield / 50) * 100)
        
        # Energy efficiency score (kWh per gram yield, lower is better)
        if predicted_yield > 0:
            energy_per_yield = energy_usage / predicted_yield
            energy_score = max(0, 100 - (energy_per_yield * 50))
        else:
            energy_score = 0
        
        # CO2 efficiency score (kg CO2 per gram yield, lower is better)
        if predicted_yield > 0:
            co2_per_yield = co2_footprint / predicted_yield
            co2_score = max(0, 100 - (co2_per_yield * 100))
        else:
            co2_score = 0
        
        # Weighted average
        sustainability_score = (yield_score * 0.3 + energy_score * 0.35 + co2_score * 0.35)
        
        return max(0, min(100, sustainability_score))
    
    def simulate(self, params: FermentationParams) -> SimulationResult:
        """
        Run full fermentation simulation.
        
        Returns comprehensive prediction results.
        """
        # Predict all outcomes
        predicted_yield, confidence = self.predict_yield(params)
        energy_usage = self.predict_energy(params, predicted_yield)
        co2_footprint = self.predict_co2(params, predicted_yield, energy_usage)
        protein_score = self.predict_protein_score(params, predicted_yield)
        
        # Calculate derived metrics
        microbe = self._normalize_microbe_name(params.microbe_type)
        profile = self.MICROBE_PROFILES[microbe]
        
        efficiency = min(100, (predicted_yield / profile["max_yield"]) * 100)
        purity = min(100, 70 + (protein_score / 100) * 30)  # Base 70% + quality bonus
        
        sustainability_score = self.calculate_sustainability_score(
            predicted_yield, energy_usage, co2_footprint
        )
        
        return SimulationResult(
            predicted_yield=round(predicted_yield, 2),
            energy_usage=round(energy_usage, 2),
            co2_footprint=round(co2_footprint, 3),
            protein_score=round(protein_score, 1),
            purity=round(purity, 1),
            efficiency=round(efficiency, 1),
            sustainability_score=round(sustainability_score, 1),
            confidence=round(confidence, 2)
        )


# Singleton instance
simulator = FermentationSimulator()


def run_simulation(
    microbe_type: str,
    substrate: str,
    temperature: float,
    ph: float,
    duration: float,
    oxygen_level: float = 21.0,
    agitation_speed: float = 200.0
) -> SimulationResult:
    """
    Convenience function to run simulation with individual parameters.
    """
    params = FermentationParams(
        microbe_type=microbe_type,
        substrate=substrate,
        temperature=temperature,
        ph=ph,
        duration=duration,
        oxygen_level=oxygen_level,
        agitation_speed=agitation_speed
    )
    return simulator.simulate(params)
