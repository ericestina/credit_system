async function api(url, opts={}) {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json();
}

const state = { policy: null, catalog: [] };
const el=(s,r=document)=>r.querySelector(s);

function labelForField(id) {
  const item = state.catalog.find(x => x.id === id);
  return item ? item.label : id;
}

function renderCriteriaChips() {
  const chips = el("#criteriaChips");
  chips.innerHTML = "";
  const p = state.policy;
  if (!p || !p.conditions) {
    chips.innerHTML = `<span class="text-sm text-gray-500">No policy configured.</span>`;
    return;
  }

  for (const c of p.conditions) {
    let text = "";
    if (c.operator === "between") text = `${labelForField(c.field)}: ${c.value[0]}–${c.value[1]}`;
    else if (c.operator === "gte") text = `${labelForField(c.field)}: ≥ ${c.value}`;
    else if (c.operator === "lte") text = `${labelForField(c.field)}: ≤ ${c.value}`;
    else if (c.operator === "eq") text = `${labelForField(c.field)}: = ${c.value}`;
    else if (c.operator === "neq") text = `${labelForField(c.field)}: ≠ ${c.value}`;
    else if (c.operator === "in") text = `${labelForField(c.field)}: in {${c.value.join(", ")}}`;
    else if (c.operator === "not_in") text = `${labelForField(c.field)}: not in {${c.value.join(", ")}}`;
    const badge = document.createElement("span");
    badge.className = "inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm";
    badge.textContent = text;
    chips.appendChild(badge);
  }

  // Hints
  const ageCond = p.conditions.find(c => c.field === "age");
  const incCond = p.conditions.find(c => c.field === "income");
  el("#hintAge").textContent = ageCond ? humanizeCond(ageCond) : "";
  el("#hintIncome").textContent = incCond ? humanizeCond(incCond) : "";
}

function humanizeCond(c) {
  if (!c) return "";
  if (c.operator === "between") return `Rule: ${c.value[0]} to ${c.value[1]}`;
  if (c.operator === "gte") return `Rule: minimum ${c.value}`;
  if (c.operator === "lte") return `Rule: maximum ${c.value}`;
  if (c.operator === "in")  return `Allowed: ${c.value.join(", ")}`;
  if (c.operator === "not_in") return `Not allowed: ${c.value.join(", ")}`;
  return `Rule: ${c.operator} ${Array.isArray(c.value) ? c.value.join(", ") : c.value}`;
}

function passesSingle(fieldValue, cond) {
  const v = fieldValue;
  switch (cond.operator) {
    case "between": return v >= Number(cond.value[0]) && v <= Number(cond.value[1]);
    case "gte":     return v >= Number(cond.value);
    case "lte":     return v <= Number(cond.value);
    case "eq":      return v == cond.value;
    case "neq":     return v != cond.value;
    case "in":      return cond.value.includes(v);
    case "not_in":  return !cond.value.includes(v);
    default:        return true;
  }
}

function localPrecheck(payload) {
  if (!state.policy || !state.policy.conditions) return { ok: true, fail: null };
  const map = { age: Number(payload.age), income: Number(payload.income), country: payload.country || null };
  for (const cond of state.policy.conditions) {
    const val = map[cond.field];
    if (val === null || val === undefined) continue;
    if (!passesSingle(val, cond)) return { ok: false, fail: cond };
  }
  return { ok: true, fail: null };
}

function showPrecheck(res) {
  const box = el("#precheckBox");
  box.classList.remove("hidden");
  if (res.ok) {
    box.className = "mt-4 p-3 rounded-lg bg-green-50 text-green-700";
    box.textContent = "Looks eligible based on the visible rules. Submit to confirm.";
  } else {
    box.className = "mt-4 p-3 rounded-lg bg-yellow-50 text-yellow-700";
    box.textContent = `Heads up: it may fail on "${labelForField(res.fail.field)}" (${humanizeCond(res.fail)}).`;
  }
}

async function submitApplication(e) {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {
    name: (fd.get("name") || "").trim(),
    age: Number(fd.get("age")),
    income: Number(fd.get("income")),
    country: (fd.get("country") || "").trim() || null,
  };

  showPrecheck(localPrecheck(payload));

  const result = await api("/api/apply", { method: "POST", body: JSON.stringify(payload) });
  const badge = el("#decisionBadge");
  const resultBox = el("#resultBox");
  const ok = result.status === "Approved";
  badge.textContent = ok ? "Approved" : "Denied";
  badge.className = `mt-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${ok ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`;
  el("#reason").textContent = result.decision_reason || "";
  el("#resultJson").textContent = JSON.stringify(result, null, 2);
  resultBox.classList.remove("hidden");
}

async function init() {
  state.catalog = await api("/api/rules");
  state.policy  = await api("/api/policy/latest").catch(() => null);
  el("#policyName").textContent = state.policy?.name ? `(${state.policy.name})` : "(no policy)";
  renderCriteriaChips();
  el("#applyForm").addEventListener("submit", (e) => submitApplication(e).catch(err => alert(err.message)));
  el("#btnCheck").addEventListener("click", () => {
    const fd = new FormData(el("#applyForm"));
    const payload = {
      name: (fd.get("name") || "").trim(),
      age: Number(fd.get("age")),
      income: Number(fd.get("income")),
      country: (fd.get("country") || "").trim() || null,
    };
    showPrecheck(localPrecheck(payload));
  });
}

document.addEventListener("DOMContentLoaded", () => {
  init().catch(err => alert(err.message));
});
