"""
FermaGen AI - Experiment Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ExperimentCreate(BaseModel):
    """Schema for creating a new experiment"""
    name: str = Field(..., min_length=2, max_length=255)
    microbe_type: str = Field(..., description="Type of microorganism")
    substrate: str = Field(..., description="Carbon source")
    temperature: float = Field(..., ge=15, le=60, description="Temperature in Celsius")
    ph: float = Field(..., ge=3, le=10, description="pH level")
    duration: float = Field(..., ge=1, le=168, description="Duration in hours")
    oxygen_level: float = Field(21.0, ge=0, le=100, description="O2 percentage")
    agitation_speed: float = Field(200.0, ge=0, le=500, description="Agitation in RPM")
    use_realtime_data: bool = Field(False, description="Fetch properties from live APIs")
    protein_name: Optional[str] = Field(None, description="Target protein to produce")
    organism: Optional[str] = Field(None, description="Organism source for UniProt")
    predict_structure: bool = Field(False, description="Run ESMFold prediction")


class ExperimentResponse(BaseModel):
    """Schema for experiment data"""
    id: int
    name: str
    microbe_type: str
    substrate: str
    temperature: float
    ph: float
    duration: float
    oxygen_level: float
    agitation_speed: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResultResponse(BaseModel):
    """Schema for simulation results"""
    id: int
    experiment_id: int
    predicted_yield: float
    energy_usage: float
    co2_footprint: float
    protein_score: float
    purity: float
    efficiency: float
    sustainability_score: float
    explanation: Optional[str]
    recommendations: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ExperimentWithResult(BaseModel):
    """Combined experiment and result"""
    experiment: ExperimentResponse
    result: Optional[ResultResponse]


class ExperimentListResponse(BaseModel):
    """Paginated experiment list"""
    experiments: List[ExperimentWithResult]
    total: int
    page: int
    per_page: int


class MicrobeInfo(BaseModel):
    """Information about a microbe type"""
    name: str
    display_name: str
    optimal_temp: float
    optimal_ph: float
    max_yield: float
    description: str


class SubstrateInfo(BaseModel):
    """Information about a substrate"""
    name: str
    display_name: str
    energy: float
    description: str


class FoodTypeInfo(BaseModel):
    """Information about a food type category"""
    name: str
    display_name: str
    description: str
    icon: str
    related_microbes: List[str]
    related_substrates: List[str]


class MicrobeWithFoodContext(BaseModel):
    """Microbe information with food context"""
    name: str
    display_name: str
    optimal_temp: float
    optimal_ph: float
    max_yield: float
    description: str
    role: str
    food_types: List[str]


class SubstrateWithFoodContext(BaseModel):
    """Substrate information with food context"""
    name: str
    display_name: str
    energy: float
    description: str
    food_types: List[str]
