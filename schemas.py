# schemas.py
from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field

# ===== Policy (rich) =====
class RuleClause(BaseModel):
    field: str
    op: str = Field(..., description="eq, ne, lt, lte, gt, gte, in, not_in, between, exists")
    value: Optional[Union[int, float, str, List[Union[int, float, str]]]] = None

class RuleBlock(BaseModel):
    id: str
    type: str = Field(..., description="eligibility | affordability | risk_threshold | pricing | override")
    description: Optional[str] = None
    when: Optional[Dict[str, List[RuleClause]]] = Field(default_factory=dict)  # all/any/none
    then: List[Dict[str, Any]] = Field(default_factory=list)
    else_: Optional[List[Dict[str, Any]]] = Field(default=None, alias="else")
    class Config:
        populate_by_name = True

class PolicyPayload(BaseModel):
    name: str
    priority: int = 10
    active: bool = True
    rules: List[RuleBlock]

class PolicyOut(PolicyPayload):
    id: int
    class Config:
        from_attributes = True

# ===== Logistic model =====
class LogRegFeature(BaseModel):
    name: str
    coef: float

class LogRegPayload(BaseModel):
    name: str
    intercept: float
    features: List[LogRegFeature]
    positive_class: str = "approve"
    threshold: float = 0.5
    imputation: Optional[Dict[str, Union[int, float]]] = None
    transform: Optional[Dict[str, Dict[str, Union[str, float]]]] = None
    metadata: Optional[Dict[str, Any]] = None

# ===== Application (apply) =====
class ApplicationIn(BaseModel):
    name: str
    age: int
    income: float
    country: Optional[str] = None

class ApplicationOut(ApplicationIn):
    id: int
    status: str
    decision_reason: str
    prob_approve: float | None = None
    prob_default: float | None = None
    apr: float | None = None
    limit_amount: float | None = None
    policy: Optional[str] = None
    model: Optional[str] = None
    class Config:
        from_attributes = True
