# routes/routes_legacy.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Policy
from schemas import PolicyOut
from .routes_policy import RULES_CATALOG

legacy = APIRouter(prefix="/api", tags=["legacy-compat"])

@legacy.get("/rules")
def legacy_rules_catalog():
    return RULES_CATALOG

@legacy.get("/policy/latest", response_model=PolicyOut | None)
def legacy_policy_latest(db: Session = Depends(get_db)):
    p = (
        db.query(Policy)
        .filter(Policy.active == 1)
        .order_by(Policy.priority.desc(), Policy.id.desc())
        .first()
    )
    return None if not p else PolicyOut.model_validate(p.blob | {"id": p.id})

