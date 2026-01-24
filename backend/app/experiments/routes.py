"""
FermaGen AI - Experiment Routes
API endpoints for fermentation experiments
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.database import get_db, User, Experiment, Result
from app.auth.utils import get_current_user
from app.experiments.schemas import (
    ExperimentCreate,
    ExperimentResponse,
    ResultResponse,
    ExperimentWithResult,
    ExperimentListResponse,
    MicrobeInfo,
    SubstrateInfo
)
from app.experiments.simulation import (
    FermentationSimulator,
    FermentationParams,
    run_simulation
)

router = APIRouter()
simulator = FermentationSimulator()


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
    
    # Run simulation
    try:
        params = FermentationParams(
            microbe_type=experiment_data.microbe_type,
            substrate=experiment_data.substrate,
            temperature=experiment_data.temperature,
            ph=experiment_data.ph,
            duration=experiment_data.duration,
            oxygen_level=experiment_data.oxygen_level,
            agitation_speed=experiment_data.agitation_speed
        )
        sim_result = simulator.simulate(params)
        
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
            recommendations=None
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
