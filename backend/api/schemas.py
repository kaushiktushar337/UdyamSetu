from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: Optional[str] = None
    business_id: Optional[str] = None
    location_id: Optional[str] = None
    available_capital: float = Field(ge=0)
    funding_available: float = Field(default=0, ge=0)
    interests: str = ""
    skills: str = ""
    experience_years: float = Field(default=0, ge=0)
    available_resources: List[str] = Field(default_factory=list)
    infrastructure: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    preferences: str = ""
    asuse_overrides: Dict[str, Any] = Field(default_factory=dict)
    planned_workers: Optional[float] = Field(default=None, ge=0)
    business_age_years: Optional[float] = Field(default=None, ge=0)
    daily_work_hours: Optional[float] = Field(default=None, ge=0, le=24)
    top_k: int = Field(default=5, ge=1, le=20)
    persist: bool = False


class AnalyzeResponse(BaseModel):
    analysis_id: Optional[str] = None
    business: Dict[str, Any]
    decision: Dict[str, Any]
    scores: Dict[str, Any]
    asuse: Optional[Dict[str, Any]] = None
    funding: Optional[Dict[str, Any]] = None
    strengths: List[str]
    concerns: List[str]
    recommendations: List[str]
    match: Dict[str, Any]
    engine_version: str
    persisted: bool = False
    # Enhanced response fields for actionable guidance
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Top 2-3 alternative recommendations with reasoning")
    market_context: Optional[Dict[str, Any]] = Field(default=None, description="Local market intelligence from ASUSE/ISES data")
    operational_guidance: Optional[Dict[str, Any]] = Field(default=None, description="Infrastructure, staffing, timeline requirements")
    next_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Prioritized action items with links")
