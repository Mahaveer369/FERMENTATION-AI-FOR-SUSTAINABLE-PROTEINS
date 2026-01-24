"""
FermaGen AI - Protein Analysis Module
BioPython-based protein sequence analysis
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import re


@dataclass
class ProteinAnalysisResult:
    """Results from protein sequence analysis"""
    sequence_length: int
    molecular_weight: float  # Daltons
    isoelectric_point: float  # pI
    amino_acid_composition: Dict[str, float]
    hydrophobicity: float  # GRAVY score
    instability_index: float
    is_stable: bool
    aromaticity: float
    charge_at_ph7: float
    secondary_structure_tendency: Dict[str, float]


class ProteinAnalyzer:
    """
    Protein sequence analyzer using BioPython-inspired calculations.
    Provides molecular weight, pI, amino acid composition, and other properties.
    """
    
    # Amino acid molecular weights (Daltons)
    AA_WEIGHTS = {
        'A': 89.09, 'R': 174.20, 'N': 132.12, 'D': 133.10, 'C': 121.15,
        'E': 147.13, 'Q': 146.15, 'G': 75.07, 'H': 155.16, 'I': 131.17,
        'L': 131.17, 'K': 146.19, 'M': 149.21, 'F': 165.19, 'P': 115.13,
        'S': 105.09, 'T': 119.12, 'W': 204.23, 'Y': 181.19, 'V': 117.15
    }
    
    # Hydrophobicity values (Kyte-Doolittle scale)
    HYDROPHOBICITY = {
        'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
        'E': -3.5, 'Q': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
        'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
        'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
    }
    
    # pKa values for pI calculation
    PK_VALUES = {
        'N_term': 9.69,
        'C_term': 2.34,
        'D': 3.86, 'E': 4.25, 'H': 6.00, 'C': 8.33,
        'Y': 10.07, 'K': 10.53, 'R': 12.48
    }
    
    # Instability index weights
    INSTABILITY_WEIGHTS = {
        'WW': 1.0, 'WC': 1.0, 'WM': 24.68, 'WH': 24.68,
        'GG': 13.34, 'MG': 1.0, 'AG': 1.0, 'VG': -7.49,
        # Simplified weights for common dipeptides
    }
    
    # Secondary structure propensities (simplified)
    HELIX_PROPENSITY = {
        'A': 1.45, 'R': 0.79, 'N': 0.73, 'D': 0.98, 'C': 0.77,
        'E': 1.53, 'Q': 1.17, 'G': 0.53, 'H': 1.24, 'I': 1.00,
        'L': 1.34, 'K': 1.07, 'M': 1.20, 'F': 1.12, 'P': 0.59,
        'S': 0.79, 'T': 0.82, 'W': 1.14, 'Y': 0.61, 'V': 1.14
    }
    
    SHEET_PROPENSITY = {
        'A': 0.97, 'R': 0.90, 'N': 0.65, 'D': 0.80, 'C': 1.30,
        'E': 0.26, 'Q': 1.23, 'G': 0.81, 'H': 0.71, 'I': 1.60,
        'L': 1.22, 'K': 0.74, 'M': 1.67, 'F': 1.28, 'P': 0.62,
        'S': 0.72, 'T': 1.20, 'W': 1.19, 'Y': 1.29, 'V': 1.65
    }
    
    def __init__(self):
        self.water_mass = 18.015  # Daltons
    
    def validate_sequence(self, sequence: str) -> tuple[bool, str]:
        """Validate protein sequence"""
        sequence = sequence.upper().replace(" ", "").replace("\n", "")
        
        if not sequence:
            return False, "Empty sequence"
        
        valid_aa = set(self.AA_WEIGHTS.keys())
        invalid_chars = set(sequence) - valid_aa
        
        if invalid_chars:
            return False, f"Invalid amino acids: {', '.join(invalid_chars)}"
        
        return True, sequence
    
    def calculate_molecular_weight(self, sequence: str) -> float:
        """Calculate molecular weight in Daltons"""
        weight = sum(self.AA_WEIGHTS.get(aa, 0) for aa in sequence)
        # Subtract water for each peptide bond
        weight -= self.water_mass * (len(sequence) - 1)
        return round(weight, 2)
    
    def calculate_amino_acid_composition(self, sequence: str) -> Dict[str, float]:
        """Calculate amino acid percentage composition"""
        total = len(sequence)
        composition = {}
        
        for aa in self.AA_WEIGHTS.keys():
            count = sequence.count(aa)
            composition[aa] = round((count / total) * 100, 2) if total > 0 else 0
        
        return composition
    
    def calculate_hydrophobicity(self, sequence: str) -> float:
        """Calculate GRAVY (Grand Average of Hydropathy)"""
        if not sequence:
            return 0.0
        
        total = sum(self.HYDROPHOBICITY.get(aa, 0) for aa in sequence)
        return round(total / len(sequence), 3)
    
    def calculate_isoelectric_point(self, sequence: str) -> float:
        """Calculate isoelectric point (pI) using bisection method"""
        # Count charged residues
        aa_counts = {aa: sequence.count(aa) for aa in 'DEHCYKR'}
        
        def charge_at_ph(ph: float) -> float:
            """Calculate net charge at given pH"""
            charge = 0.0
            
            # N-terminus (positive)
            charge += 1.0 / (1.0 + 10 ** (ph - self.PK_VALUES['N_term']))
            
            # C-terminus (negative)
            charge -= 1.0 / (1.0 + 10 ** (self.PK_VALUES['C_term'] - ph))
            
            # Acidic residues (negative)
            for aa in 'DE':
                if aa in aa_counts:
                    pka = self.PK_VALUES.get(aa, 4.0)
                    charge -= aa_counts[aa] / (1.0 + 10 ** (pka - ph))
            
            # Basic residues (positive)
            for aa in 'HKR':
                if aa in aa_counts:
                    pka = self.PK_VALUES.get(aa, 10.0)
                    charge += aa_counts[aa] / (1.0 + 10 ** (ph - pka))
            
            # Cysteine and Tyrosine
            for aa in 'CY':
                if aa in aa_counts:
                    pka = self.PK_VALUES.get(aa, 8.0)
                    charge -= aa_counts[aa] / (1.0 + 10 ** (pka - ph))
            
            return charge
        
        # Bisection method to find pI
        low, high = 0.0, 14.0
        while high - low > 0.01:
            mid = (low + high) / 2
            if charge_at_ph(mid) > 0:
                low = mid
            else:
                high = mid
        
        return round((low + high) / 2, 2)
    
    def calculate_instability_index(self, sequence: str) -> tuple[float, bool]:
        """
        Calculate instability index.
        Proteins with II > 40 are considered unstable.
        """
        if len(sequence) < 2:
            return 0.0, True
        
        # Simplified calculation using dipeptide weights
        total = 0.0
        for i in range(len(sequence) - 1):
            dipeptide = sequence[i:i+2]
            total += self.INSTABILITY_WEIGHTS.get(dipeptide, 1.0)
        
        ii = (10.0 / len(sequence)) * total
        is_stable = ii < 40
        
        return round(ii, 2), is_stable
    
    def calculate_aromaticity(self, sequence: str) -> float:
        """Calculate relative frequency of aromatic amino acids (F, W, Y)"""
        if not sequence:
            return 0.0
        
        aromatic_count = sum(1 for aa in sequence if aa in 'FWY')
        return round(aromatic_count / len(sequence), 4)
    
    def calculate_charge_at_ph7(self, sequence: str) -> float:
        """Calculate net charge at pH 7"""
        positive = sequence.count('R') + sequence.count('K')
        negative = sequence.count('D') + sequence.count('E')
        
        # Histidine is partially protonated at pH 7
        partial_positive = sequence.count('H') * 0.1
        
        return round(positive + partial_positive - negative, 2)
    
    def calculate_secondary_structure_tendency(self, sequence: str) -> Dict[str, float]:
        """Calculate tendency for secondary structure elements"""
        if not sequence:
            return {"helix": 0.0, "sheet": 0.0, "coil": 0.0}
        
        helix_sum = sum(self.HELIX_PROPENSITY.get(aa, 1.0) for aa in sequence)
        sheet_sum = sum(self.SHEET_PROPENSITY.get(aa, 1.0) for aa in sequence)
        
        helix_avg = helix_sum / len(sequence)
        sheet_avg = sheet_sum / len(sequence)
        
        # Normalize to percentages
        total = helix_avg + sheet_avg + 1.0  # Coil as baseline
        
        return {
            "helix": round((helix_avg / total) * 100, 1),
            "sheet": round((sheet_avg / total) * 100, 1),
            "coil": round((1.0 / total) * 100, 1)
        }
    
    def analyze(self, sequence: str) -> ProteinAnalysisResult:
        """
        Perform full protein analysis.
        
        Args:
            sequence: Amino acid sequence (one-letter codes)
        
        Returns:
            ProteinAnalysisResult with all calculated properties
        """
        # Validate and clean sequence
        is_valid, cleaned = self.validate_sequence(sequence)
        if not is_valid:
            raise ValueError(cleaned)
        
        sequence = cleaned
        instability, is_stable = self.calculate_instability_index(sequence)
        
        return ProteinAnalysisResult(
            sequence_length=len(sequence),
            molecular_weight=self.calculate_molecular_weight(sequence),
            isoelectric_point=self.calculate_isoelectric_point(sequence),
            amino_acid_composition=self.calculate_amino_acid_composition(sequence),
            hydrophobicity=self.calculate_hydrophobicity(sequence),
            instability_index=instability,
            is_stable=is_stable,
            aromaticity=self.calculate_aromaticity(sequence),
            charge_at_ph7=self.calculate_charge_at_ph7(sequence),
            secondary_structure_tendency=self.calculate_secondary_structure_tendency(sequence)
        )


# Singleton instance
protein_analyzer = ProteinAnalyzer()
