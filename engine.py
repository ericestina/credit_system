# engine.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import math

# ---------- transforms ----------
def _log1p(x: float) -> float:
    return math.log1p(max(float(x), 0.0))

def _clip(x: float, min_v: Optional[float], max_v: Optional[float]) -> float:
    x = float(x)
    if min_v is not None: x = max(x, float(min_v))
    if max_v is not None: x = min(x, float(max_v))
    return x

def _standardize(x: float, mean: float, std: float) -> float:
    x = float(x)
    if std == 0: return 0.0
    return (x - float(mean)) / float(std)

def apply_transform(value: Any, spec: Optional[Dict[str, Any]]) -> Any:
    if spec is None or value is None: return value
    t = spec.get("type")
    if t == "log1p": return _log1p(value)
    if t == "clip": return _clip(value, spec.get("min"), spec.get("max"))
    if t == "standardize": return _standardize(value, spec.get("mean", 0.0), spec.get("std", 1.0))
    return value

def prepare_features(payload: Dict[str, Any], model_row) -> Dict[str, float]:
    x: Dict[str, float] = {}
    feats: List[Dict[str, Any]] = model_row.features or []
    impute = model_row.imputation or {}
    transform = model_row.transform or {}
    for cf in feats:
        fname = cf["name"]
        v = payload.get(fname, impute.get(fname))
        v = apply_transform(v, transform.get(fname))
        if v is None: v = 0.0
        x[fname] = float(v)
    return x

def logistic_prob_approve(intercept: float, feats: List[Dict[str, Any]], x: Dict[str, float]) -> float:
    z = float(intercept)
    for cf in feats:
        z += float(cf["coef"]) * float(x.get(cf["name"], 0.0))
    return 1.0 / (1.0 + math.exp(-z))

# ---------- rule engine ----------
def eval_condition(value: Any, op: str, expected: Any) -> bool:
    if op == "eq": return value == expected
    if op == "ne": return value != expected
    if op == "lt": return value < expected
    if op == "lte": return value <= expected
    if op == "gt": return value > expected
    if op == "gte": return value >= expected
    if op == "in": return isinstance(expected, list) and value in expected
    if op == "not_in": return isinstance(expected, list) and value not in expected
    if op == "between": return isinstance(expected, list) and len(expected) == 2 and expected[0] <= value <= expected[1]
    if op == "exists": return (value is not None) == bool(expected)
    return False

def match_when(when: Dict[str, List[Dict[str, Any]]], ctx: Dict[str, Any]) -> bool:
    def clause_ok(c: Dict[str, Any]) -> bool:
        v = ctx.get(c["field"])
        return eval_condition(v, c["op"], c.get("value"))
    all_ok = all(clause_ok(c) for c in when.get("all", [])) if "all" in when else True
    any_ok = any(clause_ok(c) for c in when.get("any", [])) if "any" in when else True
    none_ok = not any(clause_ok(c) for c in when.get("none", [])) if "none" in when else True
    return all_ok and any_ok and none_ok

def resolve_apr_tier(table: List[Dict[str, Any]], ctx: Dict[str, Any]) -> Optional[float]:
    pd = ctx.get("prob_default", 1.0)
    for row in table:
        cond = row.get("if")
        if cond and "prob_default_lte" in cond and pd <= cond["prob_default_lte"]:
            return float(row["apr"])
    for row in table:
        if row.get("else"):
            return float(row["apr"])
    return None

def evaluate_policy(policy_blob: Dict[str, Any], ctx: Dict[str, Any]):
    decision = None
    reasons: List[str] = []
    apr: Optional[float] = None
    limit_amt: Optional[float] = None

    for rule in policy_blob.get("rules", []):
        hit = match_when((rule.get("when") or {}), ctx)
        actions = rule.get("then") if hit else (rule.get("else") or [])
        for a in actions or []:
            act = a.get("action")
            if act == "reject":
                decision = "REJECT"; reasons.append(a.get("reason", rule.get("id", "RULE")))
            elif act == "allow":
                decision = decision or "APPROVE"
            elif act == "set_limit_max":
                mult = (a.get("value") or {}).get("mult_income", 0)
                income = ctx.get("income", ctx.get("income_monthly", 0))
                calc = float(income) * float(mult)
                limit_amt = calc if limit_amt is None else min(limit_amt, calc)
            elif act == "set_apr":
                apr = float(a.get("value"))
            elif act == "set_apr_tier":
                apr = resolve_apr_tier(a.get("table", []), ctx)
            elif act == "add_reason" and a.get("reason"):
                reasons.append(a["reason"])

        if rule.get("type") == "eligibility" and decision == "REJECT":
            break

    if decision is None:
        thr = ctx.get("threshold", 0.5)
        decision = "APPROVE" if ctx.get("prob_approve", 0) >= thr else "REJECT"

    return decision, reasons, limit_amt, apr
