async function api(url, opts={}) {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json();
}
const state = { catalog: [] };
const el=(s,r=document)=>r.querySelector(s);
const els=(s,r=document)=>[...r.querySelectorAll(s)];

function setVisibilityForType(row, type){
  els(".numeric-block",row).forEach(x=>x.classList.toggle("hidden", type!=="numeric"));
  els(".categorical-block",row).forEach(x=>x.classList.toggle("hidden", type!=="categorical"));
}
function populateFieldOptions(select){
  select.innerHTML="";
  state.catalog.forEach(item=>{
    const opt=document.createElement("option");
    opt.value=item.id; opt.textContent=item.label; opt.dataset.type=item.type;
    select.appendChild(opt);
  });
}
function createRow(defaultFieldId){
  const tpl=el("#rowTemplate").content.cloneNode(true);
  const row=tpl.firstElementChild;
  const fieldSelect=el("select.field",row);
  populateFieldOptions(fieldSelect);
  if(defaultFieldId) fieldSelect.value=defaultFieldId;
  const item=state.catalog.find(x=>x.id===fieldSelect.value);
  setVisibilityForType(row, item?.type || "numeric");
  fieldSelect.addEventListener("change", ()=>{
    const it=state.catalog.find(x=>x.id===fieldSelect.value);
    setVisibilityForType(row, it?.type || "numeric");
  });
  el(".btnRemove",row).addEventListener("click", ()=>row.remove());
  return row;
}
function collectConditions(){
  const rows=els("#criteriaList > div");
  const conditions=[];
  for(const row of rows){
    const field=el("select.field",row).value;
    const type=(state.catalog.find(x=>x.id===field)||{}).type;
    if(type==="numeric"){
      const minRaw=el("input.min",row).value.trim();
      const maxRaw=el("input.max",row).value.trim();
      const hasMin=minRaw!==""; const hasMax=maxRaw!=="";
      if(!hasMin && !hasMax) continue;
      if(hasMin && hasMax) conditions.push({ field, operator:"between", value:[Number(minRaw), Number(maxRaw)] });
      else if(hasMin)      conditions.push({ field, operator:"gte", value:Number(minRaw) });
      else                 conditions.push({ field, operator:"lte", value:Number(maxRaw) });
    } else {
      const op=el("select.cat-operator",row).value;
      const vals=el("input.cat-values",row).value.split(",").map(s=>s.trim()).filter(Boolean);
      if(vals.length===0) continue;
      conditions.push({ field, operator:op, value:vals });
    }
  }
  return conditions;
}
async function savePolicy(){
  const payload={ name:"Policy configurada pelo analista", conditions:collectConditions() };
  if(payload.conditions.length===0){ alert("Adicione pelo menos um critério."); return; }
  const saved=await api("/api/policy",{ method:"POST", body:JSON.stringify(payload) });
  el("#debug").textContent=JSON.stringify(saved,null,2);
  alert("Política salva com sucesso!");
}
async function init(){
  state.catalog=await api("/api/rules");
  const list=el("#criteriaList");
  list.appendChild(createRow("age"));
  list.appendChild(createRow("income"));
  el("#btnAdd").addEventListener("click", ()=>list.appendChild(createRow()));
  el("#btnSave").addEventListener("click", ()=>savePolicy().catch(e=>alert(e.message)));
}
document.addEventListener("DOMContentLoaded", ()=>init().catch(e=>alert(e.message)));
