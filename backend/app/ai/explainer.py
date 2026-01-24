"""
FermaGen AI - AI Explanation Generator
Uses Perplexity API for generating scientific explanations
"""
import httpx
from typing import Dict, Optional
import json

from app.config import get_settings
from app.experiments.simulation import SimulationResult

settings = get_settings()


class AIExplainer:
    """
    AI-powered explanation generator for fermentation results.
    Uses Perplexity API to generate scientific, human-readable explanations.
    """
    
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    
    def __init__(self):
        self.api_key = settings.perplexity_api_key
        self.model = "llama-3.1-sonar-small-128k-online"  # Fast, free-tier friendly
    
    async def generate_explanation(
        self,
        params: Dict,
        result: SimulationResult,
        microbe: str,
        substrate: str
    ) -> str:
        """
        Generate AI explanation for fermentation results.
        
        If Perplexity API is not available, falls back to rule-based explanation.
        """
        if not self.api_key:
            return self._generate_fallback_explanation(params, result, microbe, substrate)
        
        try:
            return await self._call_perplexity(params, result, microbe, substrate)
        except Exception as e:
            print(f"Perplexity API error: {e}")
            return self._generate_fallback_explanation(params, result, microbe, substrate)
    
    async def _call_perplexity(
        self,
        params: Dict,
        result: SimulationResult,
        microbe: str,
        substrate: str
    ) -> str:
        """Call Perplexity API for explanation"""
        prompt = f"""You are a fermentation scientist. Explain these simulation results in 2-3 paragraphs:

Microbe: {microbe}
Substrate: {substrate}
Temperature: {params.get('temperature', 30)}°C
pH: {params.get('ph', 6)}
Duration: {params.get('duration', 48)} hours

Results:
- Predicted Yield: {result.predicted_yield} g/L
- Energy Usage: {result.energy_usage} kWh
- CO2 Footprint: {result.co2_footprint} kg
- Protein Quality Score: {result.protein_score}/100
- Sustainability Score: {result.sustainability_score}/100

Explain:
1. Why these conditions produced this yield
2. How to improve sustainability
3. One key optimization suggestion

Be concise and scientific."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a fermentation scientist providing concise technical analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.PERPLEXITY_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def _generate_fallback_explanation(
        self,
        params: Dict,
        result: SimulationResult,
        microbe: str,
        substrate: str
    ) -> str:
        """Generate rule-based explanation when API is unavailable"""
        explanation_parts = []
        
        # Yield analysis
        if result.predicted_yield > 30:
            explanation_parts.append(
                f"The high predicted yield of {result.predicted_yield} g/L indicates optimal growth conditions "
                f"for {microbe} on {substrate}. The temperature of {params.get('temperature', 30)}°C and "
                f"pH of {params.get('ph', 6)} are conducive to efficient substrate utilization."
            )
        elif result.predicted_yield > 15:
            explanation_parts.append(
                f"The moderate yield of {result.predicted_yield} g/L suggests room for optimization. "
                f"Consider adjusting temperature or pH closer to the optimal range for {microbe}."
            )
        else:
            explanation_parts.append(
                f"The yield of {result.predicted_yield} g/L is below typical ranges. "
                f"The current conditions may be suboptimal for {microbe} metabolism."
            )
        
        # Sustainability analysis
        if result.sustainability_score > 70:
            explanation_parts.append(
                f"With a sustainability score of {result.sustainability_score}/100, this process "
                f"demonstrates strong environmental performance. The CO2 footprint of {result.co2_footprint} kg "
                f"is efficient for the yield achieved."
            )
        else:
            explanation_parts.append(
                f"The sustainability score of {result.sustainability_score}/100 indicates potential for "
                f"environmental improvements. Consider optimizing energy usage or exploring renewable substrates."
            )
        
        # Optimization suggestion
        if params.get('duration', 48) > 72:
            explanation_parts.append(
                "Recommendation: The extended fermentation duration increases energy costs. "
                "Consider fed-batch strategies or strain engineering for faster growth."
            )
        elif result.protein_score < 75:
            explanation_parts.append(
                "Recommendation: Protein quality could be improved by optimizing expression conditions "
                "or adding chaperone co-expression."
            )
        else:
            explanation_parts.append(
                "Recommendation: Current parameters are well-balanced. Minor adjustments to agitation "
                "or oxygen levels may further improve yields."
            )
        
        return " ".join(explanation_parts)
    
    async def generate_comparison(
        self,
        results: list[Dict],
        focus: str = "sustainability"
    ) -> str:
        """Generate comparison explanation for multiple experiments"""
        if not results:
            return "No experiments to compare."
        
        if len(results) == 1:
            return "Single experiment - no comparison available."
        
        # Find best by focus
        if focus == "yield":
            sorted_results = sorted(results, key=lambda x: x.get("yield", 0), reverse=True)
            best = sorted_results[0]
            comparison = f"Experiment with highest yield ({best.get('yield', 0)} g/L) "
        elif focus == "sustainability":
            sorted_results = sorted(results, key=lambda x: x.get("sustainability_score", 0), reverse=True)
            best = sorted_results[0]
            comparison = f"Most sustainable experiment (score: {best.get('sustainability_score', 0)}) "
        else:
            sorted_results = sorted(results, key=lambda x: x.get("co2", float('inf')))
            best = sorted_results[0]
            comparison = f"Lowest CO2 experiment ({best.get('co2', 0)} kg) "
        
        comparison += f"used {best.get('microbe', 'unknown')} at {best.get('temperature', 0)}°C."
        
        return comparison


# Singleton instance
explainer = AIExplainer()
