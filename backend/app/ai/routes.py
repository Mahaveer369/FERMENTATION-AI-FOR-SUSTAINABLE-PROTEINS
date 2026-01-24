"""
FermaGen AI - AI Routes
API endpoints for optimization and AI explanations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db, User, Experiment, Result
from app.auth.utils import get_current_user
from app.ai.optimizer import optimizer, OptimizationResult
from app.ai.explainer import explainer
from app.experiments.simulation import FermentationParams, FermentationSimulator

router = APIRouter()
simulator = FermentationSimulator()


class OptimizeRequest(BaseModel):
    """Request for optimization"""
    microbe: str = Field(..., description="Microbe type")
    substrate: str = Field(..., description="Substrate type")
    baseline_temperature: Optional[float] = Field(None, description="Current temperature")
    baseline_ph: Optional[float] = Field(None, description="Current pH")
    baseline_duration: Optional[float] = Field(None, description="Current duration")
    constraints: Optional[Dict] = Field(None, description="Parameter constraints")
    weights: Optional[Dict] = Field(None, description="Objective weights")


class OptimizeResponse(BaseModel):
    """Response from optimization"""
    optimal_params: Dict[str, float]
    predicted_outcomes: Dict[str, float]
    pareto_solutions: List[Dict]
    improvement_over_baseline: Dict[str, float]
    trade_offs: str
    recommendations: List[str]


class ExplainRequest(BaseModel):
    """Request for AI explanation"""
    experiment_id: int


class ExplainResponse(BaseModel):
    """Response with AI explanation"""
    explanation: str
    experiment_id: int


class QuickSimulationRequest(BaseModel):
    """Quick simulation without saving"""
    microbe: str
    substrate: str
    temperature: float = Field(..., ge=15, le=60)
    ph: float = Field(..., ge=3, le=10)
    duration: float = Field(..., ge=1, le=168)


class QuickSimulationResponse(BaseModel):
    """Quick simulation results"""
    yield_g_per_l: float
    energy_kwh: float
    co2_kg: float
    protein_score: float
    sustainability_score: float
    efficiency: float


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_formulation(
    request: OptimizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run multi-objective optimization for fermentation parameters.
    
    Optimizes for:
    - Maximum yield
    - Minimum time
    - Minimum CO2 footprint
    
    Returns Pareto-optimal solutions and recommendations.
    """
    baseline = None
    if request.baseline_temperature is not None:
        baseline = {
            "temperature": request.baseline_temperature,
            "ph": request.baseline_ph or 6.0,
            "duration": request.baseline_duration or 48.0,
            "oxygen_level": 21.0,
            "agitation_speed": 200.0
        }
    
    try:
        result = optimizer.optimize(
            microbe=request.microbe,
            substrate=request.substrate,
            baseline_params=baseline,
            constraints=request.constraints,
            weights=request.weights
        )
        
        return OptimizeResponse(
            optimal_params=result.optimal_params,
            predicted_outcomes=result.predicted_outcomes,
            pareto_solutions=result.pareto_solutions,
            improvement_over_baseline=result.improvement_over_baseline,
            trade_offs=result.trade_offs,
            recommendations=result.recommendations
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/explain", response_model=ExplainResponse)
async def generate_explanation(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered explanation for an experiment's results.
    
    Uses Perplexity API if available, otherwise falls back to rule-based explanation.
    """
    # Get experiment
    exp_result = await db.execute(
        select(Experiment).where(
            Experiment.id == request.experiment_id,
            Experiment.user_id == current_user.id
        )
    )
    experiment = exp_result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # Get result
    result_query = await db.execute(
        select(Result).where(Result.experiment_id == request.experiment_id)
    )
    result = result_query.scalar_one_or_none()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found for this experiment"
        )
    
    # Generate explanation
    from app.experiments.simulation import SimulationResult
    
    sim_result = SimulationResult(
        predicted_yield=result.predicted_yield,
        energy_usage=result.energy_usage,
        co2_footprint=result.co2_footprint,
        protein_score=result.protein_score,
        purity=result.purity,
        efficiency=result.efficiency,
        sustainability_score=result.sustainability_score,
        confidence=0.85
    )
    
    params = {
        "temperature": experiment.temperature,
        "ph": experiment.ph,
        "duration": experiment.duration,
        "oxygen_level": experiment.oxygen_level,
        "agitation_speed": experiment.agitation_speed
    }
    
    explanation = await explainer.generate_explanation(
        params=params,
        result=sim_result,
        microbe=experiment.microbe_type,
        substrate=experiment.substrate
    )
    
    # Save explanation to result
    result.explanation = explanation
    await db.commit()
    
    return ExplainResponse(
        explanation=explanation,
        experiment_id=request.experiment_id
    )


@router.post("/quick-simulate", response_model=QuickSimulationResponse)
async def quick_simulation(request: QuickSimulationRequest):
    """
    Run a quick simulation without saving to database.
    
    Useful for exploring parameter space before committing to an experiment.
    No authentication required.
    """
    params = FermentationParams(
        microbe_type=request.microbe,
        substrate=request.substrate,
        temperature=request.temperature,
        ph=request.ph,
        duration=request.duration,
        oxygen_level=21.0,
        agitation_speed=200.0
    )
    
    result = simulator.simulate(params)
    
    return QuickSimulationResponse(
        yield_g_per_l=result.predicted_yield,
        energy_kwh=result.energy_usage,
        co2_kg=result.co2_footprint,
        protein_score=result.protein_score,
        sustainability_score=result.sustainability_score,
        efficiency=result.efficiency
    )


@router.get("/sustainability-tips")
async def get_sustainability_tips():
    """Get general sustainability improvement tips for fermentation"""
    return {
        "tips": [
            {
                "category": "Substrate",
                "tip": "Use waste-derived substrates like glycerol or agricultural residues to reduce CO2 footprint by up to 30%."
            },
            {
                "category": "Energy",
                "tip": "Optimize agitation speed - excessive mixing increases energy use without proportional yield benefits."
            },
            {
                "category": "Temperature",
                "tip": "Operating at ambient temperature when possible eliminates heating/cooling energy costs."
            },
            {
                "category": "Duration",
                "tip": "Fed-batch strategies can achieve higher yields in shorter times, reducing overall resource consumption."
            },
            {
                "category": "Microbe Selection",
                "tip": "GRAS organisms like Saccharomyces cerevisiae often have lower downstream processing requirements."
            }
        ]
    }
