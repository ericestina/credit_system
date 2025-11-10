async function getJSON(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`${res.status} ${res.statusText} - ${msg}`);
  }
  return res.json();
}

async function createDefaultPolicy() {
  const payload = {
    name: "Default Policy",
    conditions: [
      { field: "age",    operator: "gte", value: 20 },
      { field: "income", operator: "gte", value: 1000 },
      { field: "country",operator: "in",  value: ["IE", "PT", "BR"] }
    ]
  };
  const data = await getJSON("/api/policy", {
    method: "POST",
    body: JSON.stringify(payload)        // <- array mesmo, nada de JSON dentro de string!
  });
  return data;
}

async function loadLatestPolicy() {
  const data = await getJSON("/api/policy/latest");
  document.querySelector("#latestPolicy").textContent =
    data ? JSON.stringify(data, null, 2) : "Nenhuma policy criada.";
}

async function handleApply(e) {
  e.preventDefault();
  const fd = new FormData(e.target);
  const app = {
    name: fd.get("name"),
    age: Number(fd.get("age")),
    income: Number(fd.get("income")),
    country: fd.get("country") || null
  };
  const result = await getJSON("/api/apply", {
    method: "POST",
    body: JSON.stringify(app)
  });
  document.querySelector("#applyResult").textContent = JSON.stringify(result, null, 2);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("#btnDefaultPolicy").addEventListener("click", async () => {
    try {
      await createDefaultPolicy();
      await loadLatestPolicy();
      alert("Policy criada com sucesso.");
    } catch (err) {
      alert(err.message);
    }
  });

  document.querySelector("#applyForm").addEventListener("submit", (e) => {
    handleApply(e).catch(err => alert(err.message));
  });

  loadLatestPolicy().catch(() => {});
});
