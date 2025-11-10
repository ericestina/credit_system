# routes/routes_policy.py
from fastapi import APIRouter, Depends, HTTPException   # 👈 precisa do Depends aqui
from sqlalchemy.orm import Session

from database import get_db
from models import Policy
from schemas import PolicyPayload, PolicyOut

router = APIRouter(prefix="/api/policies", tags=["policies"])

RULES_CATALOG = [
    {"id": "age", "label": "Age", "type": "numeric",
     "allowed_operators": ["gte","lte","between","lt","gt","eq"], "ui":"range", "metadata":{"min":18,"max":120}},
    {"id": "income", "label": "Monthly Income", "type": "numeric",
     "allowed_operators": ["gte","lte","between","lt","gt","eq"], "ui":"range", "metadata":{"min":0,"max":1_000_000}},
    {"id": "country", "label": "Country of residence", "type": "categorical",
     "allowed_operators": ["in","not_in","eq","ne"], "ui":"select",
     "metadata":{"options":["IE","BR","PT","ES","FR","DE","US"]}},
]

@router.get("/rules-catalog")
def get_rules_catalog():
    return RULES_CATALOG

@router.post("", response_model=PolicyOut)
def save_policy(payload: PolicyPayload, db: Session = Depends(get_db)):
    row = Policy(
        name=payload.name,
        priority=payload.priority,
        active=1 if payload.active else 0,
        blob=payload.model_dump()
    )
    db.add(row); db.commit(); db.refresh(row)
    return PolicyOut.model_validate(row.blob | {"id": row.id})

@router.post("/activate/{name}")
def activate_policy(name: str, db: Session = Depends(get_db)):
    db.query(Policy).update({Policy.active: 0})
    q = db.query(Policy).filter(Policy.name == name)
    if not q.first():
        raise HTTPException(404, "Policy not found")
    q.update({Policy.active: 1}); db.commit()
    return {"ok": True, "active_policy": name}

@router.get("/active", response_model=PolicyOut | None)
def get_active_policy(db: Session = Depends(get_db)):
    p = db.query(Policy).filter(Policy.active == 1).order_by(Policy.priority.desc(), Policy.id.desc()).first()
    return None if not p else PolicyOut.model_validate(p.blob | {"id": p.id})
