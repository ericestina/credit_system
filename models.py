# models.py
from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

# === Logistic model versions ===
class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    intercept = Column(Float)
    features = Column(JSON)                 # [{"name": str, "coef": float}]
    imputation = Column(JSON, nullable=True)  # {feature: value}
    transform = Column(JSON, nullable=True)   # {feature: {type, ...}}
    positive_class = Column(String, default="approve")
    threshold = Column(Float, default=0.5)
    metadata_blob = Column(JSON, nullable=True)
    active = Column(Integer, default=1)       # 1 active / 0 inactive

# === Dynamic policy (rich JSON) ===
class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    priority = Column(Integer, nullable=False, default=10)
    active = Column(Integer, default=1)
    blob = Column(JSON, nullable=False)  # política completa como JSON

# === Decision log (usamos Application como "log") ===
class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    # input
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    country = Column(String, nullable=True)
    # output/decision
    status = Column(String, nullable=False)           # Approved / Denied
    decision_reason = Column(String, nullable=False)  # reasons resumidos
    # audit extras
    prob_approve = Column(Float, nullable=True)
    prob_default = Column(Float, nullable=True)
    apr = Column(Float, nullable=True)
    limit_amount = Column(Float, nullable=True)
    policy_name = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
