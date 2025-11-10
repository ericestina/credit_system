from sqlalchemy.orm import Session
from . import models, schemas
import json

def save_policy(db: Session, payload: schemas.PolicyCreate):
    obj = models.Policy(name=payload.name, conditions=payload.model_dump_json())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_latest_policy(db: Session):
    return db.query(models.Policy).order_by(models.Policy.id.desc()).first()

def evaluate_condition(app, cond):
    attr = getattr(app, cond.field, None)
    op = cond.operator
    val = cond.value

    if op == "gte": return attr >= val
    if op == "lte": return attr <= val
    if op == "eq": return attr == val
    if op == "neq": return attr != val
    if op == "between" and isinstance(val, list) and len(val) == 2:
        return val[0] <= attr <= val[1]
    if op == "in": return attr in val
    if op == "not_in": return attr not in val
    return False

def evaluate_policy(policy, app_data):
    try:
        conds = json.loads(policy.conditions) if isinstance(policy.conditions, str) else policy.conditions
        for c in conds:
            if not evaluate_condition(app_data, schemas.RuleCondition(**c)):
                return False, f"Falhou: {c['field']} ({c['operator']})"
        return True, "OK"
    except Exception as e:
        return False, str(e)

def create_application(db: Session, app_data: schemas.ApplicationIn, policy: models.Policy):
    ok, reason = evaluate_policy(policy, app_data)
    status = "Approved" if ok else "Denied"

    obj = models.Application(
        name=app_data.name,
        age=app_data.age,
        income=app_data.income,
        country=app_data.country,
        status=status,
        decision_reason=reason,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
