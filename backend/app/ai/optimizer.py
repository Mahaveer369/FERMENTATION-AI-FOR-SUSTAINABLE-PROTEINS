"""
FermaGen AI - Multi-Objective Optimizer
Optimizes fermentation parameters for yield, time, and sustainability
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from app.experiments.simulation import FermentationSimulator, FermentationParams, SimulationResult


@dataclass
class OptimizationResult:
    """Result from multi-objective optimization"""
    optimal_params: Dict[str, float]
    predicted_outcomes: Dict[str, float]
    pareto_solutions: List[Dict]
    improvement_over_baseline: Dict[str, float]
    trade_offs: str
    recommendations: List[str]


class FermentationOptimizer:
    """
    Multi-objective optimizer for fermentation parameters.
    
    Objectives:
    - Maximize yield
    - Minimize time (duration)
    - Minimize CO2 footprint
    
    Uses genetic algorithm approach with Pareto optimization.
    """
    
    def __init__(self):
        self.simulator = FermentationSimulator()
        self.population_size = 50
        self.generations = 30
        self.mutation_rate = 0.1
    
    def _generate_random_params(
        self,
        microbe: str,
        substrate: str,
        constraints: Optional[Dict] = None
    ) -> Dict[str, float]:
        """Generate random parameter set within constraints"""
        constraints = constraints or {}
        
        return {
            "temperature": np.random.uniform(
                constraints.get("temp_min", 20),
                constraints.get("temp_max", 45)
            ),
            "ph": np.random.uniform(
                constraints.get("ph_min", 4),
                constraints.get("ph_max", 8)
            ),
            "duration": np.random.uniform(
                constraints.get("duration_min", 12),
                constraints.get("duration_max", 96)
            ),
            "oxygen_level": np.random.uniform(
                constraints.get("o2_min", 10),
                constraints.get("o2_max", 40)
            ),
            "agitation_speed": np.random.uniform(
                constraints.get("rpm_min", 100),
                constraints.get("rpm_max", 400)
            )
        }
    
    def _evaluate(
        self,
        params: Dict[str, float],
        microbe: str,
        substrate: str
    ) -> Tuple[float, float, float]:
        """
        Evaluate objective functions.
        Returns (yield, -duration, -co2) for maximization.
        """
        ferm_params = FermentationParams(
            microbe_type=microbe,
            substrate=substrate,
            temperature=params["temperature"],
            ph=params["ph"],
            duration=params["duration"],
            oxygen_level=params["oxygen_level"],
            agitation_speed=params["agitation_speed"]
        )
        
        result = self.simulator.simulate(ferm_params)
        
        # Return objectives (we want to maximize, so negate minimization objectives)
        return (
            result.predicted_yield,
            -params["duration"],  # Minimize duration
            -result.co2_footprint  # Minimize CO2
        )
    
    def _dominates(self, a: Tuple, b: Tuple) -> bool:
        """Check if solution a dominates solution b"""
        at_least_one_better = False
        for i in range(len(a)):
            if a[i] < b[i]:
                return False
            if a[i] > b[i]:
                at_least_one_better = True
        return at_least_one_better
    
    def _get_pareto_front(
        self,
        solutions: List[Tuple[Dict, Tuple]]
    ) -> List[Tuple[Dict, Tuple]]:
        """Extract Pareto-optimal solutions"""
        pareto = []
        
        for sol in solutions:
            is_dominated = False
            for other in solutions:
                if other != sol and self._dominates(other[1], sol[1]):
                    is_dominated = True
                    break
            if not is_dominated:
                pareto.append(sol)
        
        return pareto
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Single-point crossover"""
        child = {}
        for key in parent1:
            if np.random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child
    
    def _mutate(self, params: Dict, constraints: Optional[Dict] = None) -> Dict:
        """Gaussian mutation"""
        constraints = constraints or {}
        mutated = params.copy()
        
        mutation_std = {
            "temperature": 3.0,
            "ph": 0.5,
            "duration": 12.0,
            "oxygen_level": 5.0,
            "agitation_speed": 50.0
        }
        
        bounds = {
            "temperature": (constraints.get("temp_min", 20), constraints.get("temp_max", 45)),
            "ph": (constraints.get("ph_min", 4), constraints.get("ph_max", 8)),
            "duration": (constraints.get("duration_min", 12), constraints.get("duration_max", 96)),
            "oxygen_level": (constraints.get("o2_min", 10), constraints.get("o2_max", 40)),
            "agitation_speed": (constraints.get("rpm_min", 100), constraints.get("rpm_max", 400))
        }
        
        for key in mutated:
            if np.random.random() < self.mutation_rate:
                mutated[key] += np.random.normal(0, mutation_std[key])
                mutated[key] = np.clip(mutated[key], bounds[key][0], bounds[key][1])
        
        return mutated
    
    def optimize(
        self,
        microbe: str,
        substrate: str,
        baseline_params: Optional[Dict] = None,
        constraints: Optional[Dict] = None,
        weights: Optional[Dict] = None
    ) -> OptimizationResult:
        """
        Run multi-objective optimization.
        
        Args:
            microbe: Microbe type
            substrate: Substrate type
            baseline_params: Current parameters for comparison
            constraints: Parameter bounds
            weights: Objective weights (yield, time, co2)
        
        Returns:
            OptimizationResult with optimal parameters and analysis
        """
        weights = weights or {"yield": 0.5, "time": 0.25, "co2": 0.25}
        
        # Initialize population
        population = [
            self._generate_random_params(microbe, substrate, constraints)
            for _ in range(self.population_size)
        ]
        
        # Evolution loop
        for gen in range(self.generations):
            # Evaluate all solutions
            evaluated = [
                (params, self._evaluate(params, microbe, substrate))
                for params in population
            ]
            
            # Get Pareto front
            pareto = self._get_pareto_front(evaluated)
            
            # Selection (tournament)
            offspring = []
            while len(offspring) < self.population_size:
                # Select from Pareto front preferentially
                if pareto and np.random.random() < 0.7:
                    parent1 = pareto[np.random.randint(len(pareto))][0]
                    parent2 = pareto[np.random.randint(len(pareto))][0]
                else:
                    idx1, idx2 = np.random.randint(len(evaluated), size=2)
                    parent1 = evaluated[idx1][0]
                    parent2 = evaluated[idx2][0]
                
                # Crossover and mutate
                child = self._crossover(parent1, parent2)
                child = self._mutate(child, constraints)
                offspring.append(child)
            
            population = offspring
        
        # Final evaluation
        final_evaluated = [
            (params, self._evaluate(params, microbe, substrate))
            for params in population
        ]
        pareto_front = self._get_pareto_front(final_evaluated)
        
        # Select best compromise solution using weights
        best_solution = None
        best_score = float('-inf')
        
        for params, objectives in pareto_front:
            score = (
                weights["yield"] * objectives[0] / 50 +  # Normalize
                weights["time"] * objectives[1] / 96 +
                weights["co2"] * objectives[2] / 2
            )
            if score > best_score:
                best_score = score
                best_solution = (params, objectives)
        
        # If no good solution found, use first from Pareto
        if best_solution is None:
            best_solution = pareto_front[0] if pareto_front else final_evaluated[0]
        
        optimal_params = best_solution[0]
        
        # Get full simulation result for optimal
        optimal_result = self.simulator.simulate(FermentationParams(
            microbe_type=microbe,
            substrate=substrate,
            temperature=optimal_params["temperature"],
            ph=optimal_params["ph"],
            duration=optimal_params["duration"],
            oxygen_level=optimal_params["oxygen_level"],
            agitation_speed=optimal_params["agitation_speed"]
        ))
        
        # Calculate improvement if baseline provided
        improvement = {}
        if baseline_params:
            baseline_result = self.simulator.simulate(FermentationParams(
                microbe_type=microbe,
                substrate=substrate,
                temperature=baseline_params.get("temperature", 30),
                ph=baseline_params.get("ph", 6),
                duration=baseline_params.get("duration", 48),
                oxygen_level=baseline_params.get("oxygen_level", 21),
                agitation_speed=baseline_params.get("agitation_speed", 200)
            ))
            
            if baseline_result.predicted_yield > 0:
                improvement["yield"] = round(
                    ((optimal_result.predicted_yield - baseline_result.predicted_yield) / 
                     baseline_result.predicted_yield) * 100, 1
                )
            improvement["co2"] = round(
                ((baseline_result.co2_footprint - optimal_result.co2_footprint) / 
                 baseline_result.co2_footprint) * 100 if baseline_result.co2_footprint > 0 else 0, 1
            )
            improvement["energy"] = round(
                ((baseline_result.energy_usage - optimal_result.energy_usage) / 
                 baseline_result.energy_usage) * 100 if baseline_result.energy_usage > 0 else 0, 1
            )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(optimal_params, optimal_result, microbe)
        
        # Trade-off analysis
        trade_offs = self._analyze_trade_offs(pareto_front)
        
        # Format Pareto solutions
        pareto_solutions = [
            {
                "params": p[0],
                "yield": round(p[1][0], 2),
                "duration": round(-p[1][1], 1),
                "co2": round(-p[1][2], 3)
            }
            for p in pareto_front[:5]  # Top 5
        ]
        
        return OptimizationResult(
            optimal_params={k: round(v, 2) for k, v in optimal_params.items()},
            predicted_outcomes={
                "yield": optimal_result.predicted_yield,
                "energy": optimal_result.energy_usage,
                "co2": optimal_result.co2_footprint,
                "protein_score": optimal_result.protein_score,
                "sustainability_score": optimal_result.sustainability_score
            },
            pareto_solutions=pareto_solutions,
            improvement_over_baseline=improvement,
            trade_offs=trade_offs,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        params: Dict,
        result: SimulationResult,
        microbe: str
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        profile = self.simulator.MICROBE_PROFILES.get(
            self.simulator._normalize_microbe_name(microbe),
            {}
        )
        
        # Temperature advice
        if profile:
            temp_diff = abs(params["temperature"] - profile.get("optimal_temp", 30))
            if temp_diff < 2:
                recommendations.append(
                    f"Temperature is optimal for {microbe}. Maintain at {params['temperature']:.1f}°C."
                )
            else:
                recommendations.append(
                    f"Consider adjusting temperature closer to optimal {profile.get('optimal_temp', 30)}°C."
                )
        
        # Duration advice
        if params["duration"] > 72:
            recommendations.append(
                "Extended fermentation duration increases costs. Consider fed-batch optimization."
            )
        
        # Sustainability
        if result.sustainability_score > 70:
            recommendations.append(
                f"High sustainability score ({result.sustainability_score}). Good for eco-certification."
            )
        else:
            recommendations.append(
                "Consider process optimization to improve sustainability metrics."
            )
        
        return recommendations
    
    def _analyze_trade_offs(self, pareto_front: List) -> str:
        """Analyze trade-offs in Pareto front"""
        if len(pareto_front) < 2:
            return "Single optimal solution found with no significant trade-offs."
        
        # Calculate ranges
        yields = [p[1][0] for p in pareto_front]
        durations = [-p[1][1] for p in pareto_front]
        co2s = [-p[1][2] for p in pareto_front]
        
        yield_range = max(yields) - min(yields)
        duration_range = max(durations) - min(durations)
        co2_range = max(co2s) - min(co2s)
        
        analysis = []
        if yield_range > 5:
            analysis.append(f"Yield varies by {yield_range:.1f} g/L across optimal solutions.")
        if duration_range > 12:
            analysis.append(f"Duration can vary by {duration_range:.0f} hours with trade-offs.")
        if co2_range > 0.2:
            analysis.append(f"CO2 footprint ranges by {co2_range:.2f} kg across options.")
        
        return " ".join(analysis) if analysis else "Trade-offs are minimal between objectives."


# Singleton instance
optimizer = FermentationOptimizer()
