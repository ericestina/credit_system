# routes_models.py
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from database import get_db
from models import ModelVersion
from schemas import LogRegPayload

router = APIRouter(prefix="/api/models", tags=["models"])

@router.post("/logreg")
def upload_logreg(model: LogRegPayload, db: Session = Depends(get_db)):
    # desativa versões anteriores
    db.query(ModelVersion).update({ModelVersion.active: 0})
    m = ModelVersion(
        name=model.name,
        intercept=model.intercept,
        features=[{"name": f.name, "coef": f.coef} for f in model.features],
        imputation=model.imputation,
        transform=model.transform,
        positive_class=model.positive_class,
        threshold=model.threshold,
        metadata_blob=model.metadata,
        active=1
    )
    db.add(m); db.commit(); db.refresh(m)
    return {"ok": True, "model": m.name}

@router.post("/activate/{name}")
def activate_model(name: str, db: Session = Depends(get_db)):
    q = db.query(ModelVersion).filter(ModelVersion.name == name)
    if not q.first():
        raise HTTPException(404, "Model not found")
    db.query(ModelVersion).update({ModelVersion.active: 0})
    q.update({ModelVersion.active: 1})
    db.commit()
    return {"ok": True, "active_model": name}

@router.get("/active")
def get_active_model(db: Session = Depends(get_db)):
    m = db.query(ModelVersion).filter(ModelVersion.active == 1).first()
    if not m: return None
    return {
        "name": m.name,
        "intercept": m.intercept,
        "features": m.features,
        "positive_class": m.positive_class,
        "threshold": m.threshold,
        "active": m.active,
    }
# routes/routes_models.py
@router.get("/models/active")
def get_active_model(db: Session = Depends(get_db)):
    m = db.query(ModelVersion).filter(ModelVersion.active == 1).order_by(ModelVersion.id.desc()).first()
    if not m: return None
    return {
        "id": m.id,
        "name": m.name,
        "intercept": m.intercept,
        "features": m.features,
        "imputation": m.imputation,
        "transform": m.transform,
        "positive_class": m.positive_class,
        "threshold": m.threshold,
        "metadata": m.metadata,
        "active": m.active,
    }

@router.get("/models/active")
def get_active_model(db: Session = Depends(get_db)):
    m = (db.query(ModelVersion)
          .filter(ModelVersion.active == 1)
          .order_by(ModelVersion.id.desc())
          .first())
    if not m:
        return None
    return {
        "id": m.id,
        "name": m.name,
        "intercept": m.intercept,
        "features": m.features,
        "imputation": m.imputation,
        "transform": m.transform,
        "positive_class": m.positive_class,
        "threshold": m.threshold,
        "metadata": m.metadata,
        "active": m.active,
    }