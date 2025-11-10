# routes_score.py
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from database import get_db
from models import Application, Policy, ModelVersion
from schemas import ApplicationIn, ApplicationOut
from engine import prepare_features, logistic_prob_approve, evaluate_policy

router = APIRouter(prefix="/api", tags=["apply"])

@router.post("/apply", response_model=ApplicationOut)
def apply(app_data: ApplicationIn, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.active == 1).order_by(Policy.priority.desc(), Policy.id.desc()).first()
    if not policy: raise HTTPException(400, "No active policy configured.")
    model = db.query(ModelVersion).filter(ModelVersion.active == 1).first()
    if not model: raise HTTPException(400, "No active model configured.")

    # score
    x = prepare_features(app_data.dict(), model)
    prob_approve = logistic_prob_approve(model.intercept, model.features or [], x)
    prob_default = 1.0 - prob_approve

    # policy
    ctx = {
        **app_data.dict(),
        **x,
        "prob_approve": prob_approve,
        "prob_default": prob_default,
        "threshold": model.threshold,
    }
    decision, reasons, limit_amt, apr = evaluate_policy(policy.blob, ctx)
    status = "Approved" if decision == "APPROVE" else "Denied"
    reason_txt = ", ".join(reasons) if reasons else "OK"

    row = Application(
        name=app_data.name, age=app_data.age, income=app_data.income, country=app_data.country,
        status=status, decision_reason=reason_txt,
        prob_approve=prob_approve, prob_default=prob_default, apr=apr, limit_amount=limit_amt,
        policy_name=policy.name, model_name=model.name, created_at=datetime.utcnow().isoformat()
    )
    db.add(row); db.commit(); db.refresh(row)

    return ApplicationOut(
        id=row.id, name=row.name, age=row.age, income=row.income, country=row.country,
        status=row.status, decision_reason=row.decision_reason,
        prob_approve=row.prob_approve, prob_default=row.prob_default,
        apr=row.apr, limit_amount=row.limit_amount, policy=row.policy_name, model=row.model_name
    )

@router.get("/history")
def history(limit: int = 100, db: Session = Depends(get_db)):
    q = db.query(Application).order_by(Application.id.desc()).limit(limit).all()
    return [
        {
            "id": r.id, "created_at": r.created_at, "name": r.name, "age": r.age,
            "income": r.income, "country": r.country, "status": r.status,
            "decision_reason": r.decision_reason, "prob_approve": r.prob_approve,
            "prob_default": r.prob_default, "apr": r.apr, "limit_amount": r.limit_amount,
            "policy": r.policy_name, "model": r.model_name
        } for r in q
    ]
