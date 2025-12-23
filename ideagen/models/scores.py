from typing import Dict, List, Optional
from pydantic import BaseModel

class IdeaScore(BaseModel):
    mvp_scope: str
    effort_hours: int
    effort_confidence: int
    effort_justification: str
    monthly_revenue_min: float
    monthly_revenue_max: float
    revenue_confidence: int
    revenue_justification: str
    key_assumptions: List[str]
    time_to_revenue_weeks: int
    time_to_revenue_confidence: int
    solo_feasibility_score: int
    solo_feasibility_justification: str
    tech_stack_alignment: int
    required_technologies: List[str]
    new_skills_required: List[str]
    maintenance_hours_weekly: float
    maintenance_justification: str
    business_model_score: int
    business_model_justification: str

class EnrichedIdeaScore(IdeaScore):
    roi_ratio: Optional[float] = None
    opportunity_score: Optional[float] = None
    solo_dev_verdict: Optional[str] = None
    avg_monthly_revenue: Optional[float] = None

class ScoringResponse(BaseModel):
    idea_scores: Dict[str, IdeaScore]
