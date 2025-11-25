from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Task(BaseModel):
    id: str
    name: str
    start_date: Optional[datetime]
    finish_date: Optional[datetime]
    duration: float
    percent_complete: int
    resource_names: List[str] = []
    predecessors: List[str] = []

class ProjectAnalysis(BaseModel):
    project_name: str
    total_tasks: int
    critical_path: List[str]
    resource_utilization: Dict[str, float]
    productivity_index: float
    risks: List[str]

class AgentResponse(BaseModel):
    agent_name: str
    analysis: str
    data: Dict[str, Any]

class ContractActivity(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    resource_requirements: List[str] = []
    deliverables: List[str] = []

class ProductivityMetric(BaseModel):
    resource_name: str
    assigned_tasks: int
    completed_tasks: int
    total_duration: float
    completed_duration: float
    productivity_index: float
    status: str  # "efficient", "normal", "delayed"

class ContractComparison(BaseModel):
    summary: str
    delayed_activities: List[Dict[str, Any]]
    missing_activities: List[str]
    extra_activities: List[str]
    productivity_metrics: List[ProductivityMetric]
    compliance_score: float
    recommendations: List[str]
