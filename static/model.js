// static/model.js
const tbody = document.getElementById("feat-body");
const btnAdd = document.getElementById("btn-add-feat");
const btnUpload = document.getElementById("btn-upload");
const btnActivate = document.getElementById("btn-activate");
const btnGetActive = document.getElementById("btn-get-active");
const msg = document.getElementById("m-msg");
const activePre = document.getElementById("active-json");

function row(feature="", coef=""){
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td><input placeholder="feature" value="${feature}" /></td>
    <td><input type="number" step="any" placeholder="coef" value="${coef}" /></td>
    <td class="feat-actions"><button type="button" class="del">Remove</button></td>
  `;
  tr.querySelector(".del").onclick = () => tr.remove();
  return tr;
}

// start with two example rows
tbody.appendChild(row("age", "-0.02"));
tbody.appendChild(row("income", "0.0008"));

btnAdd.onclick = () => tbody.appendChild(row());

function parseJSONorNull(txt){
  if(!txt || !txt.trim()) return null;
  try { return JSON.parse(txt); } catch(e){ return null; }
}

async function uploadModel(){
  const name = document.getElementById("m-name").value.trim();
  const intercept = parseFloat(document.getElementById("m-intercept").value);
  const positive_class = document.getElementById("m-pos").value.trim() || "approve";
  const threshold = parseFloat(document.getElementById("m-th").value || "0.5");

  const imputation = parseJSONorNull(document.getElementById("m-imputation").value);
  const transform = parseJSONorNull(document.getElementById("m-transform").value);
  const metadata = parseJSONorNull(document.getElementById("m-metadata").value);

  const features = [];
  [...tbody.querySelectorAll("tr")].forEach(tr=>{
    const f = tr.querySelectorAll("input")[0].value.trim();
    const c = parseFloat(tr.querySelectorAll("input")[1].value);
    if(f && !Number.isNaN(c)) features.push({ name: f, coef: c });
  });

  if(!name){ msg.innerHTML = `<span class="err">Model name is required.</span>`; return; }
  if(Number.isNaN(intercept)){ msg.innerHTML = `<span class="err">Intercept is required.</span>`; return; }
  if(features.length === 0){ msg.innerHTML = `<span class="err">Add at least one feature.</span>`; return; }

  const payload = { name, intercept, features, imputation, transform, positive_class, threshold, metadata };
  try{
    const res = await fetch("/api/models/logreg", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(!res.ok){ throw new Error(data.detail || JSON.stringify(data)); }
    msg.innerHTML = `<span class="ok">Model uploaded: ${data.model}</span>`;
  }catch(e){
    msg.innerHTML = `<span class="err">${e.message}</span>`;
  }
}

async function activateModel(){
  const name = document.getElementById("m-name").value.trim();
  if(!name){ msg.innerHTML = `<span class="err">Provide the model name to activate.</span>`; return; }
  try{
    const res = await fetch(`/api/models/activate/${encodeURIComponent(name)}`, { method:"POST" });
    const data = await res.json();
    if(!res.ok){ throw new Error(data.detail || JSON.stringify(data)); }
    msg.innerHTML = `<span class="ok">Active model: ${data.active_model}</span>`;
    await getActive();
  }catch(e){
    msg.innerHTML = `<span class="err">${e.message}</span>`;
  }
}

async function getActive(){
  try{
    // este endpoint precisa existir no backend (routes_models.py)
    const res = await fetch("/api/models/active");
    const data = await res.json();
    if(!res.ok){ throw new Error(data.detail || JSON.stringify(data)); }
    activePre.textContent = JSON.stringify(data || null, null, 2);
  }catch(e){
    activePre.textContent = `erro ao buscar modelo ativo: ${e.message}`;
  }
}

btnUpload.onclick = uploadModel;
btnActivate.onclick = activateModel;
btnGetActive.onclick = getActive;

// tenta carregar modelo ativo ao abrir
getActive();
