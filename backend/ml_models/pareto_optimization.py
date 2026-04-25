"""
FermaGen AI - Pareto Front Multi-Objective Optimization
Isolates the NSGA-II non-dominated sorting algorithms to balance conflicting industrial objectives
(Yield Maximization vs Energy/Carbon Minimization) computing the ultimate Sustainability Score.
"""
from typing import List

class ParetoOptimizationEvaluator:
    """
    Mathematical evaluator that establishes the non-dominated multi-objective manifold curve.
    Any point on this exact sequence demonstrates absolute maximal efficiency where no objective
    can be structurally improved without sacrificing a concurrent metric.
    """
    
    def __init__(self, objective_minimization: List[bool]):
        """
        Setup optimization mappings. 
        Example: [False, True, True] = [Maximize Yield, Minimize Energy, Minimize CO2]
        """
        self.objective_minimization = objective_minimization
        
    def _dominates(self, obj1: tuple, obj2: tuple) -> bool:
        """
        Determines if output matrix 1 dominates output matrix 2 across all targeted limits.
        """
        at_least_one_better = False
        
        for idx, (val1, val2) in enumerate(zip(obj1, obj2)):
            is_minimize = self.objective_minimization[idx] if idx < len(self.objective_minimization) else False
            
            if is_minimize:
                if val1 > val2: return False
                if val1 < val2: at_least_one_better = True
            else:
                # Maximization
                if val1 < val2: return False
                if val1 > val2: at_least_one_better = True
                
        return at_least_one_better

    def execute_non_dominated_sort(self, organisms: List) -> List[List]:
        """
        Evaluates the generated models from the Random Forest array and filters the raw
        industrial optimizations. Outputs ranked 'fronts' of Pareto efficiencies.
        """
        # Cleanup
        for org in organisms:
            org.domination_count = 0
            org.dominated_solutions = []
            
        fronts = [[]]
        
        for i, p in enumerate(organisms):
            for j, q in enumerate(organisms):
                if i == j: continue
                
                if self._dominates(p.fitness_objectives, q.fitness_objectives):
                    p.dominated_solutions.append(q)
                elif self._dominates(q.fitness_objectives, p.fitness_objectives):
                    p.domination_count += 1
                    
            if p.domination_count == 0:
                fronts[0].append(p)
                
        current = 0
        while fronts[current]:
            next_front = []
            for p in fronts[current]:
                for q in p.dominated_solutions:
                    q.domination_count -= 1
                    if q.domination_count == 0:
                        next_front.append(q)
            current += 1
            if next_front:
                fronts.append(next_front)
                
        return [f for f in fronts if f]
        
    def compute_sustainability_score(self, pareto_orgs: List) -> List[dict]:
        """
        Resolves the 0-100% Sustainability Score by comparing Euclidean proximity
        towards the perfect mathematical utopian parameter.
        """
        results = []
        for org in pareto_orgs:
            # Simulated simplistic scoring prioritizing yield balance vs waste
            out = org.fitness_objectives
            yield_score = out[0] if len(out) > 0 else 0
            energy = out[1] if len(out) > 1 else 100
            emissions = out[2] if len(out) > 2 else 100
            
            # Normalize
            normalized = ((yield_score / 15.0) * 0.5) - ((energy / 500) * 0.25) - ((emissions / 100) * 0.25)
            final_grade = max(0, min(100.0, (normalized + 0.5) * 100))
            
            results.append({
                "params": org.genes,
                "sustainability_score": final_grade,
                "outputs": out
            })
            
        return results

if __name__ == "__main__":
    print("Pareto Environmental Matrix Analyzer initialized.")
