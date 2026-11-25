(function(){
"use strict";
// Ensure dependencies loaded
const PACKAGES = window.ADVISOR_PACKAGES;
const SERVICES = window.ADVISOR_SERVICES;
const State = window.AdvisorState;
const Engine = window.AdvisorEngine;

if(!PACKAGES || !State || !Engine){
  console.error("Advisor dependencies missing");
  return;
}

// Helpers
function el(id){ return document.getElementById(id); }
function qs(sel,ctx){ return (ctx||document).querySelector(sel); }
function qsa(sel,ctx){ return Array.from((ctx||document).querySelectorAll(sel)); }

// ---------- Wizard Flow Definitions ----------
const FLOWS = {
  none: [
    { id:"storeName", q:"عندك اسم للمتجر؟", hint:"يساعدنا نحدد إذا تحتاج حجز دومين وهوية", type:"single", options:[
      {value:"yes", label:"نعم", emoji:"✅"},
      {value:"no", label:"لا", emoji:"❌"},
      {value:"idea", label:"عندي فكرة فقط", emoji:"💡"}
    ], field:"storeNameStatus" },
    { id:"logo", q:"عندك شعار وهوية؟", hint:"الشعار والهوية يأثرون على تكلفة الباقة", type:"single", options:[
      {value:"yes", label:"نعم جاهزة", emoji:"🎨"},
      {value:"onlyLogo", label:"عندي شعار فقط", emoji:"🖼️"},
      {value:"no", label:"لا", emoji:"❌"}
    ], field:"hasLogo" },
    { id:"productsReady", q:"منتجاتك جاهزة؟", hint:"المنتجات والصور أهم جزء قبل الإطلاق", type:"single", options:[
      {value:"yes", label:"نعم", emoji:"📦"},
      {value:"partial", label:"بعضها", emoji:"📝"},
      {value:"no", label:"لا", emoji:"⏳"}
    ], field:"productsReady" },
    { id:"productsCount", q:"تقريبًا كم منتج؟", hint:"عدد المنتجات يحدد الباقة المناسبة", type:"single", options:[
      {value:"<10", label:"أقل من 10", emoji:"🔢"},
      {value:"10-20", label:"10 إلى 20", emoji:"📊"},
      {value:"20-35", label:"20 إلى 35", emoji:"📈"},
      {value:"more", label:"أكثر", emoji:"🚀"},
      {value:"unknown", label:"ما أعرف حتى الآن", emoji:"❓"}
    ], field:"productsCount" },
    { id:"budget", q:"وش تفضل؟", hint:"اختر المستوى اللي يناسب ميزانيتك ووقتك", type:"single", options:[
      {value:"basic", label:"أبي أجهز الأشياء الأساسية فقط", emoji:"🛠️"},
      {value:"pro", label:"أبي متجر احترافي", emoji:"⭐"},
      {value:"full", label:"أبي أسلمكم كل شيء وتسلّموني متجر جاهز", emoji:"👑"}
    ], field:"budgetPreference", after: (val, state)=>{
      if(val==="full") state.needsFullSetup = true;
      if(val==="basic") state.needsFullSetup = false;
    } }
  ],
  new: [
    { id:"platform", q:"متجرك على أي منصة؟", hint:"سلة و زد لهم تجهيزات مختلفة", type:"single", options:[
      {value:"salla", label:"سلة", emoji:"🟢"},
      {value:"zid", label:"زد", emoji:"🔵"},
      {value:"unknown", label:"غير متأكد", emoji:"❓"}
    ], field:"platform" },
    { id:"prepared", q:"وش الأشياء اللي جهزتها؟", hint:"اختر كل اللي جهزته — تقدر تختار أكثر من واحد", type:"multi", options:[
      {value:"logo", label:"الشعار"},
      {value:"products", label:"المنتجات"},
      {value:"payment", label:"الدفع"},
      {value:"shipping", label:"الشحن"},
      {value:"domain", label:"الدومين"},
      {value:"design", label:"التصميم"},
      {value:"none", label:"ما جهزت شيء تقريبًا", exclusive:true}
    ], field:"preparedItems" },
    { id:"goal", q:"وش هدفك الآن؟", hint:"هدفك يحدد نوع العمل اللي نحتاجه", type:"single", options:[
      {value:"design", label:"أبي شكل احترافي", emoji:"🎨"},
      {value:"sell", label:"أبي أجهزه للبيع", emoji:"💰"},
      {value:"full", label:"أبي شخص يستلمه كامل", emoji:"👑"},
      {value:"unknown", label:"مو عارف وش ناقص", emoji:"❓"}
    ], field:"goal" }
  ],
  existing: [
    { id:"issues", q:"وش أكثر شيء مو عاجبك؟", hint:"اختر الأهم — تقدر تختار أكثر من واحد لو حاب", type:"multi", options:[
      {value:"design", label:"شكل المتجر"},
      {value:"home", label:"الصفحة الرئيسية"},
      {value:"mobile", label:"نسخة الجوال"},
      {value:"banners", label:"البنرات"},
      {value:"products", label:"المنتجات"},
      {value:"seo", label:"SEO — تحسين ظهور متجرك في Google", tooltip:"SEO — تحسين ظهور متجرك في Google"},
      {value:"speed", label:"سرعة المتجر"},
      {value:"payment_shipping", label:"الدفع والشحن"},
      {value:"tracking", label:"التتبع والإعلانات — ربط أدوات تتبع الإعلانات"},
      {value:"full", label:"أبي تطوير شامل", exclusive:true},
      {value:"unknown", label:"مو عارف وين المشكلة", exclusive:true}
    ], field:"issues" },
    { id:"storeUrl", q:"هل تقدر ترسل رابط متجرك؟", hint:"اختياري — يساعدنا نفهم وضعك بدقة", type:"input", inputType:"url", placeholder:"https://example.com أو salla.sa/...", optional:true, field:"storeUrl" }
  ],
  specific: [
    { id:"services", q:"وش الخدمات اللي تحتاجها؟", hint:"اختر كل اللي تحتاجه — خدمة أو أكثر", type:"multi-services", options: SERVICES.map(s=> ({value:s.id, label:s.label, desc:s.desc, tooltip:s.tooltip})) , field:"requestedServices" }
  ],
  unknown: [
    { id:"storeStatusAsk", q:"أول شيء، عندك متجر حاليًا؟", hint:"سؤال سريع عشان نحدد المسار", type:"single", options:[
      {value:"none", label:"ما عندي متجر", emoji:"🌱"},
      {value:"new", label:"عندي متجر جديد", emoji:"🛒"},
      {value:"existing", label:"عندي متجر وأبي أطوره", emoji:"🚀"},
      {value:"specific", label:"أبي خدمة محددة فقط", emoji:"🎯"}
    ], field:"storeStatus", after: (val, state)=>{
      // if they pick a path, we will branch into that flow next
    } }
  ]
};

// Map initial entry card id to flow key
const ENTRY_TO_FLOW = { none:"none", new:"new", existing:"existing", specific:"specific", unknown:"unknown" };

// ---------- State & DOM refs ----------
let currentFlowKey = null;
let currentSteps = [];
let currentStepIdx = 0;
let isTransitioning = false;

function getAdvisorSection(){
  return el("smart-advisor");
}
function getCardsGrid(){ return el("advisorCardsGrid"); }
function getWizardPanel(){ return el("wizardPanel"); }
function getWizardQuestion(){ return el("wizardQuestion"); }
function getWizardHint(){ return el("wizardHint"); }
function getWizardOptions(){ return el("wizardOptions"); }
function getWizardInputArea(){ return el("wizardInputArea"); }
function getWizardInput(){ return el("wizardInput"); }
function getWizardProgressText(){ return el("wizardProgressText"); }
function getWizardProgressFill(){ return el("wizardProgressFill"); }
function getWizardResult(){ return el("wizardResult"); }

// ---------- Init ----------
function init(){
  // Wire entry cards
  const grid = getCardsGrid();
  if(grid){
    grid.addEventListener("click", function(e){
      const card = e.target.closest(".adv-entry-card");
      if(!card) return;
      const id = card.dataset.entry;
      handleEntryClick(id);
    });
    // keyboard
    grid.addEventListener("keydown", function(e){
      if(e.key==="Enter" || e.key===" "){
        const card = e.target.closest(".adv-entry-card");
        if(card){ e.preventDefault(); handleEntryClick(card.dataset.entry); }
      }
    });
  }

  // Wire wizard buttons
  const backBtn = el("wizardBack");
  const restartBtn = el("wizardRestart");
  const continueBtn = el("wizardContinue");
  const skipBtn = el("wizardSkip");
  const inputBtn = el("wizardInputBtn");

  if(backBtn) backBtn.addEventListener("click", handleBack);
  if(restartBtn) restartBtn.addEventListener("click", handleRestart);
  if(continueBtn) continueBtn.addEventListener("click", handleContinueMulti);
  if(skipBtn) skipBtn.addEventListener("click", handleSkip);
  if(inputBtn) inputBtn.addEventListener("click", handleInputSubmit);
  const inp = getWizardInput();
  if(inp){
    inp.addEventListener("keydown", function(e){ if(e.key==="Enter") handleInputSubmit(); });
    inp.addEventListener("input", validateInput);
  }

  // Listen to state changes (from chat)
  window.addEventListener("advisor:stateChanged", function(e){
    // if wizard is open, reflect progress? but avoid loops
    // update progress fill if needed
    syncUIFromState();
  });
  window.addEventListener("advisor:reset", function(){
    resetWizardUI();
  });

  // Check resume banner
  checkResumeBanner();

  // Wire result delegated events
  const result = getWizardResult();
  if(result){
    result.addEventListener("click", handleResultClick);
  }

  // Wire chat result ask
  const askBtn = el("resultAskBtn");
  const askInput = el("resultAskInput");
  if(askBtn && askInput){
    askBtn.addEventListener("click", function(){ handleResultAsk(askInput.value); });
    askInput.addEventListener("keydown", function(e){ if(e.key==="Enter") handleResultAsk(askInput.value); });
  }

  // If state already has a flow in progress, offer resume
  const state = State.loadState();
  if(state.wizardPath && !Engine.isReadyForRecommendation(state)){
    // show resume banner already handled
  }
}

function handleEntryClick(entryId){
  if(entryId==="unknown"){
    // open chat directly per spec, but also start wizard unknown flow as fallback
    // We will start unknown wizard AND open chat
    openChat();
    startFlow("unknown");
    // track
    try{ if(window.gtag) gtag('event','advisor_start',{entry:entryId}); }catch(e){}
    return;
  }
  startFlow(entryId);
  try{ if(window.gtag) gtag('event','advisor_start',{entry:entryId}); }catch(e){}
}

function startFlow(entryId){
  const state = State.loadState();
  state.wizardPath = entryId;
  state.wizardStepIndex = 0;
  state.wizardHistory = [];
  // if entry is unknown later branches, keep storeStatus unknown initially?
  // For other flows, set storeStatus field accordingly
  if(entryId==="none") state.storeStatus="none";
  else if(entryId==="new") state.storeStatus="new";
  else if(entryId==="existing") state.storeStatus="existing";
  else if(entryId==="specific") state.storeStatus="specific";
  else if(entryId==="unknown") state.storeStatus="unknown";
  State.saveState(state);

  currentFlowKey = ENTRY_TO_FLOW[entryId];
  currentSteps = FLOWS[currentFlowKey] || [];
  currentStepIdx = 0;

  // Hide cards, show wizard
  const grid = getCardsGrid();
  const panel = getWizardPanel();
  const result = getWizardResult();
  if(grid) grid.style.display="none";
  if(result) result.classList.add("hidden");
  if(panel) panel.classList.remove("hidden");

  // Hide resume banner
  const banner = el("advResumeBanner");
  if(banner) banner.style.display="none";

  renderStep();
  // Scroll to wizard
  const sec = getAdvisorSection();
  if(sec) sec.scrollIntoView({behavior:"smooth", block:"start"});
}

function renderStep(){
  const state = State.loadState();
  // Handle branching for unknown flow first step
  if(currentFlowKey==="unknown" && currentStepIdx===1){
    // after first question, branch to actual flow
    const chosen = state.storeStatus;
    if(chosen==="none" || chosen==="new" || chosen==="existing" || chosen==="specific"){
      // switch flow
      currentFlowKey = chosen;
      currentSteps = FLOWS[chosen];
      currentStepIdx = 0;
      // keep wizardPath as original unknown but update flow
      renderStep();
      return;
    }
  }

  // Check if we've completed all steps
  if(currentStepIdx >= currentSteps.length){
    // Try to recommend
    const rec = Engine.recommend(state);
    if(rec){
      showResult(rec, state);
    } else {
      // Not enough data, ask businessType as fallback or show partial
      // For simplicity, show result with pro suggestion?
      // Ask for business type if missing
      if(!state.businessType){
        // Inject an extra step: business type free text
        currentSteps.push({
          id:"businessType",
          q:"وش نوع منتجاتك أو نشاطك؟",
          hint:"مثال: عطور، عبايات، إلكترونيات — يساعدنا نخصص التوصية",
          type:"input", inputType:"text", placeholder:"مثال: عطور", optional:true, field:"businessType"
        });
        renderStep();
        return;
      }
      const fallback = Engine.recommend(State.loadState());
      if(fallback) showResult(fallback, state);
      else showNeedMoreInfo();
    }
    return;
  }

  const step = currentSteps[currentStepIdx];
  // If step is already answered via state (from chat), skip it
  const fieldVal = state[step.field];
  const isAnswered = isFieldAnswered(fieldVal, step);
  if(isAnswered && shouldSkipIfAnswered(step, state)){
    // Auto advance but keep answer
    currentStepIdx++;
    // save step index
    state.wizardStepIndex = currentStepIdx;
    State.saveState(state);
    // Avoid infinite loop, render next
    renderStep();
    return;
  }

  // Render UI for this step
  updateProgress();
  const qEl = getWizardQuestion();
  const hintEl = getWizardHint();
  const optsEl = getWizardOptions();
  const inputArea = getWizardInputArea();
  const continueBtn = el("wizardContinue");
  const skipBtn = el("wizardSkip");

  if(qEl) qEl.textContent = step.q;
  if(hintEl) hintEl.textContent = step.hint || "";
  if(optsEl){
    optsEl.innerHTML = "";
    optsEl.className = "wizard-options";
    if(step.type==="single") optsEl.classList.add("single");
  }
  if(inputArea) inputArea.classList.add("hidden");
  if(continueBtn) continueBtn.classList.add("hidden");
  if(skipBtn) skipBtn.style.display = step.optional ? "inline-flex" : "none";

  if(step.type==="single"){
    renderSingleOptions(step, state);
  } else if(step.type==="multi" || step.type==="multi-services"){
    renderMultiOptions(step, state);
    if(continueBtn) continueBtn.classList.remove("hidden");
    updateContinueState(step);
  } else if(step.type==="input"){
    renderInputStep(step, state);
  }

  // Animate
  const body = el("wizardBody");
  if(body){
    body.classList.remove("wizard-fade");
    void body.offsetWidth;
    body.classList.add("wizard-fade");
  }

  validateStepCanContinue();
}

function isFieldAnswered(val, step){
  if(val===null || val===undefined) return false;
  if(Array.isArray(val)) return val.length>0;
  if(typeof val==="string") return val.trim().length>0;
  if(typeof val==="boolean") return true;
  return true;
}
function shouldSkipIfAnswered(step, state){
  // Don't skip if user came via wizard and wants to change? But for sync with chat, we should skip only if the field was set via chat and not yet visited in this wizard session
  // Simpler: if field already has value and currentStepIdx is not 0 and history doesn't contain this step, we can skip automatically to avoid repeating
  // But allow user to go back and edit, so we only auto-skip if the value was set externally and we haven't shown this step yet in current flow
  // Check wizardHistory: if step.id already in history, don't skip (user already answered)
  const history = state.wizardHistory || [];
  const alreadyInHistory = history.some(h=> h.stepId===step.id);
  if(alreadyInHistory) return false;
  // If field is set and we are not at first visit, skip
  return isFieldAnswered(state[step.field], step);
}

function renderSingleOptions(step, state){
  const optsEl = getWizardOptions();
  const currentVal = state[step.field];
  step.options.forEach(opt=>{
    const btn = document.createElement("button");
    btn.type="button";
    btn.className="wizard-opt";
    if(currentVal===opt.value) btn.classList.add("selected");
    btn.dataset.value = opt.value;
    // tooltip
    if(opt.tooltip) {
      btn.classList.add("svc-tooltip");
      btn.setAttribute("data-tooltip", opt.tooltip);
    }
    btn.innerHTML = `
      ${opt.emoji ? `<span class="wizard-opt-emoji">${opt.emoji}</span>` : ""}
      <span class="wizard-opt-text">
        ${opt.label}
        ${opt.desc ? `<span class="wizard-opt-sub">${opt.desc}</span>` : ""}
      </span>
    `;
    btn.addEventListener("click", ()=> handleSingleSelect(step, opt.value));
    optsEl.appendChild(btn);
  });
}

function renderMultiOptions(step, state){
  const optsEl = getWizardOptions();
  // for services, use checkbox style with two lines
  const currentVals = Array.isArray(state[step.field]) ? state[step.field] : [];
  step.options.forEach(opt=>{
    const label = document.createElement("label");
    label.className="wizard-opt";
    if(currentVals.includes(opt.value)) label.classList.add("selected");
    const isService = step.type==="multi-services";
    label.innerHTML = `
      <input type="checkbox" value="${opt.value}" ${currentVals.includes(opt.value) ? "checked" : ""} />
      <span class="wizard-opt-text">
        ${opt.label}
        ${opt.desc ? `<span class="wizard-opt-sub">${opt.desc}</span>` : ""}
      </span>
    `;
    if(opt.tooltip){
      label.classList.add("svc-tooltip");
      label.setAttribute("data-tooltip", opt.tooltip);
    }
    const cb = label.querySelector("input");
    cb.addEventListener("change", ()=> handleMultiToggle(step, opt.value, cb.checked, opt.exclusive));
    label.addEventListener("click", function(e){
      if(e.target.tagName!=="INPUT"){
        e.preventDefault();
        cb.checked = !cb.checked;
        cb.dispatchEvent(new Event("change"));
      }
    });
    optsEl.appendChild(label);
  });
}

function renderInputStep(step, state){
  const inputArea = getWizardInputArea();
  const inp = getWizardInput();
  const skipBtn = el("wizardSkip");
  if(inputArea) inputArea.classList.remove("hidden");
  if(inp){
    inp.value = state[step.field] || "";
    inp.placeholder = step.placeholder || "";
    inp.type = step.inputType==="url" ? "text" : (step.inputType||"text");
    // set inputmode
    inp.inputMode = step.inputType==="url" ? "url" : "text";
    // focus with delay for mobile
    setTimeout(()=> inp.focus(), 300);
  }
  if(skipBtn) skipBtn.style.display = "inline-flex";
  // Change button text
  const btn = el("wizardInputBtn");
  if(btn) btn.textContent = step.optional ? "متابعة" : "التالي";
}

function handleSingleSelect(step, value){
  if(isTransitioning) return;
  isTransitioning = true;
  const state = State.loadState();
  const patch = {};
  patch[step.field] = value;
  // handle after hook
  if(step.after) step.after(value, state);
  // Special for unknown first step: need to update storeStatus correctly
  if(step.field==="storeStatus" && currentFlowKey==="unknown"){
    // already set
  }
  // For hasLogo: also derive hasIdentity
  if(step.field==="hasLogo"){
    if(value==="yes") patch["hasIdentity"]=true;
    else if(value==="false" || value==="no" || value===false) patch["hasIdentity"]=false;
    else if(value==="onlyLogo") patch["hasIdentity"]=false;
  }
  if(step.field==="storeNameStatus"){
    // no extra
  }
  // Save history
  state.wizardHistory = state.wizardHistory || [];
  state.wizardHistory.push({ stepId: step.id, value, at: Date.now() });
  Object.assign(state, patch);
  state.wizardStepIndex = currentStepIdx+1;
  State.saveState(state);

  // Visual feedback
  const optsEl = getWizardOptions();
  qsa(".wizard-opt", optsEl).forEach(o=> o.classList.remove("selected"));
  const chosen = qsa(".wizard-opt", optsEl).find(o=> o.dataset.value===value);
  if(chosen) chosen.classList.add("selected");

  setTimeout(()=>{
    currentStepIdx++;
    isTransitioning=false;
    renderStep();
  }, 260);
}

function handleMultiToggle(step, value, checked, exclusive){
  const state = State.loadState();
  let arr = Array.isArray(state[step.field]) ? [...state[step.field]] : [];
  if(exclusive && checked){
    arr = [value];
  } else if(exclusive && !checked){
    arr = arr.filter(x=> x!==value);
  } else {
    if(checked){
      if(!arr.includes(value)) arr.push(value);
      // if exclusive option previously selected, remove it
      const exclusiveVals = step.options.filter(o=> o.exclusive).map(o=> o.value);
      exclusiveVals.forEach(ev=>{
        if(ev!==value) arr = arr.filter(x=> x!==ev);
      });
    } else {
      arr = arr.filter(x=> x!==value);
    }
  }
  state[step.field]=arr;
  State.saveState(state);
  // Update UI selected states
  const optsEl = getWizardOptions();
  qsa(".wizard-opt", optsEl).forEach(label=>{
    const cb = label.querySelector("input");
    if(!cb) return;
    const v = cb.value;
    if(arr.includes(v)){
      label.classList.add("selected");
      cb.checked=true;
    } else {
      label.classList.remove("selected");
      cb.checked=false;
    }
  });
  updateContinueState(step);
}

function updateContinueState(step){
  const btn = el("wizardContinue");
  if(!btn) return;
  const state = State.loadState();
  const arr = state[step.field] || [];
  btn.disabled = arr.length===0;
}

function handleContinueMulti(){
  const state = State.loadState();
  const step = currentSteps[currentStepIdx];
  const arr = state[step.field] || [];
  if(arr.length===0) return;
  // push history
  state.wizardHistory = state.wizardHistory || [];
  state.wizardHistory.push({ stepId: step.id, value: [...arr], at: Date.now() });
  state.wizardStepIndex = currentStepIdx+1;
  State.saveState(state);
  currentStepIdx++;
  renderStep();
}

function handleInputSubmit(){
  const inp = getWizardInput();
  const step = currentSteps[currentStepIdx];
  const val = (inp.value||"").trim();
  if(!val && !step.optional){
    inp.focus();
    inp.style.borderColor = "#E5484D";
    setTimeout(()=> inp.style.borderColor="", 1500);
    return;
  }
  // Validate URL if needed
  if(val && step.field==="storeUrl"){
    // allow salla.sa or any http, but not require protocol
    const ok = /^(https?:\/\/)?[a-z0-9.-]+\.[a-z]{2,}/i.test(val);
    if(!ok && val.length>0){
      showToast("تأكد من صيغة الرابط — مثال: salla.sa/store أو https://example.com");
      return;
    }
  }
  const state = State.loadState();
  state[step.field]=val;
  state.wizardHistory = state.wizardHistory || [];
  state.wizardHistory.push({ stepId: step.id, value: val, at: Date.now() });
  state.wizardStepIndex = currentStepIdx+1;
  State.saveState(state);
  currentStepIdx++;
  renderStep();
}

function handleSkip(){
  const step = currentSteps[currentStepIdx];
  const state = State.loadState();
  state.wizardHistory = state.wizardHistory || [];
  state.wizardHistory.push({ stepId: step.id, value: null, skipped:true, at: Date.now() });
  state.wizardStepIndex = currentStepIdx+1;
  State.saveState(state);
  // clear input
  const inp = getWizardInput();
  if(inp) inp.value="";
  currentStepIdx++;
  renderStep();
}

function handleBack(){
  if(currentStepIdx===0){
    // back to cards
    resetWizardUI(true);
    return;
  }
  currentStepIdx = Math.max(0, currentStepIdx-1);
  const state = State.loadState();
  state.wizardStepIndex = currentStepIdx;
  State.saveState(state);
  renderStep();
}

function handleRestart(){
  if(confirm("هل تريد البدء من جديد ومسح الإجابات؟")){
    State.resetState();
    resetWizardUI(true);
    // also clear chat
    if(window.AdvisorChat) window.AdvisorChat.clearUI && window.AdvisorChat.clearUI();
  }
}

function resetWizardUI(showCards){
  currentFlowKey=null;
  currentSteps=[];
  currentStepIdx=0;
  const grid = getCardsGrid();
  const panel = getWizardPanel();
  const result = getWizardResult();
  if(panel) panel.classList.add("hidden");
  if(result) result.classList.add("hidden");
  if(showCards && grid){
    grid.style.display="grid";
    checkResumeBanner();
  }
  // reset progress
  updateProgress();
}

function updateProgress(){
  const textEl = getWizardProgressText();
  const fillEl = getWizardProgressFill();
  if(!textEl || !fillEl) return;
  if(!currentSteps.length){
    textEl.textContent = "";
    fillEl.style.width="0%";
    return;
  }
  const total = currentSteps.length;
  const current = Math.min(currentStepIdx+1, total);
  textEl.textContent = `${current} من ${total}`;
  const pct = Math.round((current/total)*100);
  fillEl.style.width = pct+"%";
}

function syncUIFromState(){
  // If wizard is visible, ensure progress reflects state but don't force re-render to avoid jump
  // Only update continue button state for multi steps
  if(!currentSteps.length) return;
  const step = currentSteps[currentStepIdx];
  if(step && (step.type==="multi" || step.type==="multi-services")){
    updateContinueState(step);
  }
}

function checkResumeBanner(){
  const state = State.loadState();
  const banner = el("advResumeBanner");
  if(!banner) return;
  // Show if there's saved wizardPath and not yet recommended
  const hasProgress = state.wizardPath && state.wizardHistory && state.wizardHistory.length>0;
  const rec = Engine.recommend(state);
  if(hasProgress && !rec){
    banner.style.display="flex";
    const txt = el("advResumeText");
    if(txt) txt.innerHTML = `عندك إجابات محفوظة — <strong>نكمل من وين وقفنا؟</strong>`;
  } else {
    banner.style.display="none";
  }
  // wire buttons
  const contBtn = el("advResumeContinue");
  const resetBtn = el("advResumeReset");
  if(contBtn && !contBtn.dataset.wired){
    contBtn.dataset.wired="1";
    contBtn.addEventListener("click", function(){
      // resume flow
      const s = State.loadState();
      if(s.wizardPath){
        currentFlowKey = ENTRY_TO_FLOW[s.wizardPath] || s.wizardPath;
        currentSteps = FLOWS[currentFlowKey] || [];
        // find index based on history length
        currentStepIdx = s.wizardHistory ? s.wizardHistory.length : 0;
        // ensure not out of bounds
        currentStepIdx = Math.min(currentStepIdx, currentSteps.length);
        const grid = getCardsGrid();
        const panel = getWizardPanel();
        if(grid) grid.style.display="none";
        if(panel) panel.classList.remove("hidden");
        renderStep();
      }
    });
  }
  if(resetBtn && !resetBtn.dataset.wired){
    resetBtn.dataset.wired="1";
    resetBtn.addEventListener("click", handleRestart);
  }
}

function showNeedMoreInfo(){
  // Fallback: ask for business type then recommend pro
  const state = State.loadState();
  const rec = Engine.recommend(state) || { type:"package", packageId:"professional", package: PACKAGES["professional"], reasons:["تحتاج توضيح إضافي"], compare:"" };
  showResult(rec, state);
}

function showResult(rec, state){
  const grid = getCardsGrid();
  if(grid) grid.style.display="none";
  const panel = getWizardPanel();
  const resultEl = getWizardResult();
  if(panel) panel.classList.add("hidden");
  if(!resultEl) return;
  resultEl.classList.remove("hidden");
  resultEl.innerHTML = buildResultHTML(rec, state);
  const send=resultEl.querySelector("#waSendBtn");
  if(send){
    send.hidden=true;
    send.textContent="افتح واتساب بالملخص";
    const consent=document.createElement("label");
    consent.className="ez-consent result-share-consent";
    const checkbox=document.createElement("input");
    checkbox.type="checkbox";
    checkbox.addEventListener("change",()=>{send.hidden=!checkbox.checked;});
    consent.append(checkbox,document.createTextNode("أوافق على مشاركة الملخص مع إزهلها عند فتح واتساب."));
    send.parentElement.before(consent);
  }
  // update state with recommended
  const s = State.loadState();
  s.recommendedPackage = rec.packageId;
  State.saveState(s);
  // wire dynamic update for edit chips
  // scroll into view
  setTimeout(()=> resultEl.scrollIntoView({behavior:"smooth", block:"start"}), 120);
  // track
  try{ if(window.gtag) gtag('event','advisor_recommend',{pkg:rec.packageId}); }catch(e){}
  // update global WA float label
  updateGlobalCTA(rec);
}

function buildResultHTML(rec, state){
  if(rec.type==="custom"){
    const svcLabels = SERVICES.filter(s=> state.requestedServices.includes(s.id)).map(s=> s.label).join("، ");
    const waLink = Engine.buildWhatsAppLink(state, rec);
    const preview = Engine.buildWhatsAppMessage(state, rec);
    return `
      <div class="result-card">
        <div class="result-header">
          <div class="result-badge">🎯 خدمة مخصصة</div>
          <h3 class="result-package-name">خدمة مخصصة</h3>
          <p class="result-tagline">اخترت ${svcLabels} — نجهز لك عرض وتكلفة واضحة</p>
        </div>
        <div class="result-body">
          <div class="result-section">
            <div class="result-section-title"><span>📌</span> الخدمات التي اخترتها</div>
            <ul class="result-list">
              ${SERVICES.filter(s=> state.requestedServices.includes(s.id)).map(s=> `<li>${s.label} — ${s.desc}</li>`).join("")}
            </ul>
          </div>
          ${state.storeUrl ? `<div class="result-section"><div class="result-section-title"><span>🔗</span> رابط متجرك</div><p style="font-size:.86rem;color:var(--adv-secondary)">${escapeHtml(state.storeUrl)}</p></div>` : ""}
          <div class="result-section">
            <div class="result-section-title"><span>📦</span> وش نستلم منك؟</div>
            <ul class="result-list needs">
              <li>تفاصيل الخدمة وهدفك منها</li>
              <li>بيانات الدخول إذا احتاج التنفيذ داخل المنصة</li>
              <li>أي ملفات أو صور مرتبطة</li>
            </ul>
          </div>
          <div class="result-whatsapp-preview">
            <div class="result-preview-label">💬 معاينة رسالة واتساب</div>
            <div class="result-preview-text" id="waPreviewCustom">${escapeHtml(preview)}</div>
          </div>
          <div class="result-actions">
            <a href="${waLink}" target="_blank" rel="noopener" class="result-btn primary" id="waSendBtn">إرسال على واتساب ←</a>
            <button type="button" class="result-btn secondary result-edit-chip" data-edit="services">تغيير الخدمات</button>
          </div>
          <div class="result-ask-box">
            <div class="result-ask-header">💬 عندك سؤال قبل تبدأ؟</div>
            <div class="result-ask-body">
              <input id="resultAskInput" class="result-ask-input" placeholder="مثال: كم تكلفة إضافة خدمة ثانية؟" />
              <button type="button" id="resultAskBtn" class="result-ask-btn">اسأل</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  const pkg = rec.package;
  const whatWeDo = Engine.getWhatWeDo(pkg.id);
  const whatWeNeed = Engine.getWhatWeNeed(state, pkg.id);
  const after = Engine.getAfterDelivery(pkg.id);
  const waLink = Engine.buildWhatsAppLink(state, rec);
  const preview = Engine.buildWhatsAppMessage(state, rec);
  const reasons = rec.reasons || [];
  const compare = rec.compare || "";
  // Determine alternative cheaper option for button
  let altBtnLabel = "";
  let altAction = "";
  if(pkg.id==="gold"){
    altBtnLabel = "أبي أشوف خيار أرخص";
    altAction = "cheaper";
  } else if(pkg.id==="professional"){
    altBtnLabel = "قارن لي مع الذهبية";
    altAction = "compareGold";
  } else if(pkg.id==="plus"){
    altBtnLabel = "قارن لي مع الاحترافية";
    altAction = "comparePro";
  }

  return `
    <div class="result-card">
      <div class="result-header">
        <div class="result-badge">${pkg.id==="gold" ? "👑 الأكثر شمولاً" : pkg.id==="professional" ? "⭐ الأكثر طلباً" : "🌱 بداية منظمة"}</div>
        <h3 class="result-package-name">الأنسب لك — ${pkg.fullName}</h3>
        <div class="result-price">
          ${pkg.oldPrice ? `<span class="result-price-old">${pkg.oldPrice.toLocaleString()} ر</span>` : ""}
          <span class="result-price-new">${pkg.priceFormatted}</span>
          <span class="result-price-currency">ريال</span>
        </div>
        <p class="result-tagline">${escapeHtml(pkg.tagline)} — ${escapeHtml(pkg.bestFor)}</p>
        ${state.productsCount === "more" ? '<p class="result-tagline">الباقة تشمل حتى 35 منتجًا. نحدد تكلفة المنتجات الإضافية بعد مراجعة طلبك.</p>' : ''}
      </div>
      <div class="result-body">
        <div class="result-section">
          <div class="result-section-title"><span>✨</span> ليش اخترناها لك؟</div>
          <ul class="result-list">
            ${reasons.map(r=> `<li>${escapeHtml(r)}</li>`).join("")}
          </ul>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <div class="result-section">
            <div class="result-section-title"><span>📥</span> وش راح نستلم منك؟</div>
            <ul class="result-list needs">
              ${whatWeNeed.map(x=> `<li>${escapeHtml(x)}</li>`).join("")}
            </ul>
          </div>
          <div class="result-section">
            <div class="result-section-title"><span>✅</span> وش نتولى إحنا؟</div>
            <ul class="result-list">
              ${whatWeDo.slice(0,8).map(x=> `<li>${escapeHtml(x)}</li>`).join("")}
            </ul>
          </div>
        </div>

        <div class="result-section">
          <div class="result-section-title"><span>🎁</span> بعد التسليم</div>
          <div class="result-after">${escapeHtml(after)}</div>
        </div>

        ${compare ? `<div class="result-section"><div class="result-section-title"><span>⚖️</span> ليش هذه الباقة وليس غيرها؟</div><div class="result-compare">${escapeHtml(compare)}</div></div>` : ""}

        <div class="result-edit-row">
          <span style="font-size:.78rem;color:var(--adv-muted);font-weight:700;margin-left:6px">تعديل سريع:</span>
          <button type="button" class="result-edit-chip" data-edit="productsCount">تغيير عدد المنتجات</button>
          <button type="button" class="result-edit-chip" data-edit="budget">تغيير الميزانية</button>
          <button type="button" class="result-edit-chip" data-edit="reset">ابدأ من جديد</button>
        </div>

        <div class="result-whatsapp-preview">
          <div class="result-preview-label">💬 هذه المعلومات سنرسلها لليث حتى ما تضطر تعيد شرح كل شيء</div>
          <div class="result-preview-text" id="waPreviewText">${escapeHtml(preview)}</div>
        </div>

        <div class="result-actions">
          <a href="${waLink}" target="_blank" rel="noopener" class="result-btn primary" id="waSendBtn">إرسال على واتساب ←</a>
          <button type="button" class="result-btn secondary" data-alt="${altAction}">${altBtnLabel}</button>
        </div>

        <div class="result-ask-box">
          <div class="result-ask-header">💬 عندك سؤال قبل تبدأ؟</div>
          <div class="result-ask-body">
            <input id="resultAskInput" class="result-ask-input" placeholder="مثال: ليش ما تكفيني الاحترافية؟" />
            <button type="button" id="resultAskBtn" class="result-ask-btn">اسأل</button>
          </div>
          <div id="resultAskAnswer" style="padding:0 16px 14px;display:none;font-size:.86rem;color:var(--adv-secondary);line-height:1.7"></div>
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(s){
  return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function showToast(msg){
  let t = el("toast");
  if(!t){t=document.createElement("div");t.id="toast";t.className="ez-toast";t.setAttribute("role","status");document.body.append(t);}
  t.textContent=msg;
  t.classList.add("on");
  setTimeout(()=> t.classList.remove("on"), 3400);
}

function validateInput(){
  const inp = getWizardInput();
  const step = currentSteps[currentStepIdx];
  if(!inp || !step) return;
  // could add live validation
}

function handleResultClick(e){
  if(e.target.closest("#resultAskBtn")){
    handleResultAsk(el("resultAskInput")?.value || "");
    return;
  }
  const chip = e.target.closest(".result-edit-chip");
  if(chip){
    const edit = chip.dataset.edit;
    if(edit==="reset") handleRestart();
    else if(edit==="services") reopenWizardAtField("requestedServices");
    else if(edit==="productsCount") {
      // open wizard at productsCount step
      reopenWizardAtField("productsCount");
    } else if(edit==="budget"){
      reopenWizardAtField("budgetPreference");
    }
    return;
  }
  const altBtn = e.target.closest("[data-alt]");
  if(altBtn){
    const alt = altBtn.dataset.alt;
    handleAltComparison(alt);
  }
}

function reopenWizardAtField(field){
  const state = State.loadState();
  // Find flow that contains field
  let flowKey = state.wizardPath;
  if(!flowKey) flowKey = "none";
  let steps = FLOWS[flowKey] || [];
  let idx = steps.findIndex(s=> s.field===field);
  if(idx===-1){
    // search other flows
    for(const k in FLOWS){
      const i = FLOWS[k].findIndex(s=> s.field===field);
      if(i!==-1){ flowKey=k; steps=FLOWS[k]; idx=i; break; }
    }
  }
  if(idx===-1) return;
  currentFlowKey=flowKey;
  currentSteps=steps;
  currentStepIdx=idx;
  const grid = getCardsGrid();
  const panel = getWizardPanel();
  const result = getWizardResult();
  if(grid) grid.style.display="none";
  if(result) result.classList.add("hidden");
  if(panel) panel.classList.remove("hidden");
  renderStep();
}

function handleAltComparison(alt){
  const state = State.loadState();
  let newRec = null;
  if(alt==="cheaper"){
    // suggest cheaper: if gold -> professional, if pro -> plus
    const cur = state.recommendedPackage;
    if(cur==="gold"){
      // simulate budget basic
      const tmp = Object.assign({}, state, {budgetPreference:"pro", needsFullSetup:false});
      newRec = Engine.recommend(tmp);
      const diff = PACKAGES["gold"].price - PACKAGES["professional"].price;
      showToast(`لو اخترت الاحترافية بتوفر ${diff} ريال، لكن ستحتاج تتولى بنفسك: الدومين، CSS المتحرك، وبعض الإعدادات المتقدمة`);
    } else {
      showToast("هذه أرخص باقة — لا يوجد أرخص منها");
      return;
    }
  } else if(alt==="compareGold"){
    newRec = Engine.recommend(Object.assign({}, state, {budgetPreference:"full", needsFullSetup:true}));
    showToast(`الذهبية تضيف دومين مجاني، CSS متحرك، SEO متقدم، بكسلات وتوثيق — بزيادة ${PACKAGES["gold"].price - PACKAGES["professional"].price} ريال`);
  } else if(alt==="comparePro"){
    newRec = Engine.recommend(Object.assign({}, state, {budgetPreference:"pro"}));
    showToast(`الاحترافية تضيف شعار وSEO أساسي وAnalytics مقابل ${PACKAGES["professional"].price - PACKAGES["plus"].price} ريال`);
  }
  if(newRec && newRec.type==="package"){
    const result=getWizardResult();
    let comparison=el("advisorComparison");
    if(result && !comparison){comparison=document.createElement("div");comparison.id="advisorComparison";comparison.className="result-compare";comparison.setAttribute("role","status");result.append(comparison);}
    if(comparison){
      const current=PACKAGES[state.recommendedPackage] || Engine.recommend(state)?.package;
      const targetId=alt==="cheaper"?"professional":alt==="compareGold"?"gold":"professional";
      const target=PACKAGES[targetId];
      comparison.textContent=(current?`${current.fullName}: ${current.priceFormatted} ريال.\n`:"")+`${target.fullName}: ${target.priceFormatted} ريال، حتى ${target.limits.products} منتجًا.\n`+Engine.buildCompare(state,targetId);
      if(["20-35","more"].includes(state.productsCount) && target.limits.products<35) comparison.textContent+="\nهذه الباقة لا تغطي عدد منتجاتك كاملًا؛ تُراجع تكلفة المنتجات الإضافية قبل الطلب.";
      comparison.scrollIntoView({behavior:"smooth",block:"nearest"});
    }
  }
}

function handleResultAsk(question){
  if(!question || !question.trim()){
    showToast("اكتب سؤالك أولاً");
    return;
  }
  const q = question.trim();
  // Use chat to answer with context
  const state = State.loadState();
  const rec = Engine.recommend(state);
  // Append to chat and get answer via AdvisorChat
  if(window.AdvisorChat){
    window.AdvisorChat.askFromResult(q, state, rec);
  } else {
    // fallback simple answer
    const ansEl = el("resultAskAnswer");
    if(ansEl){
      ansEl.style.display="block";
      ansEl.textContent = localAnswerForResult(q, state, rec);
    }
  }
}

function localAnswerForResult(question, state, rec){
  const q = question.toLowerCase();
  if(q.includes("ليش") && q.includes("احتراف")){
    return Engine.buildCompare(state, rec.packageId);
  }
  if(q.includes("أقدر") && q.includes("شحن")){
    const next = Object.assign({}, state, {preparedItems: (state.preparedItems||[]).filter(x=> x!=="shipping")});
    // simulate they will do shipping
    const newRec = Engine.recommend(next);
    if(newRec && newRec.packageId!==rec.packageId){
      return `بما أنك ستتولى الشحن بنفسك، ${newRec.package.fullName} تصبح كافية لاحتياجك وتوفر ${rec.package.price - newRec.package.price} ريال.`;
    } else {
      return `حتى لو توليت الشحن بنفسك، ما زالت ${rec.package.fullName} الأنسب لأنك تحتاج باقي التجهيزات المتكاملة.`;
    }
  }
  if(q.includes("سعر") || q.includes("تكلفة")){
    return `سعر ${rec.package.fullName} هو ${rec.package.priceFormatted} ريال. التفاصيل كاملة في المقارنة أعلاه. إذا أردت خيار أرخص اضغط "أبي أشوف خيار أرخص".`;
  }
  return "سؤالك وصل — يمكنك فتح المحادثة الذكية لجواب مفصل حسب حالتك، أو التواصل واتساب لتوضيح مباشر.";
}

function updateGlobalCTA(rec){
  const fab = el("chatFab");
  const fabLabel = el("chatFabLabel");
  if(!fabLabel) return;
  if(rec && rec.type==="package"){
    fabLabel.textContent = `ابدأ بـ ${rec.package.name}`;
  } else if(rec && rec.type==="custom"){
    fabLabel.textContent = "أرسل طلبي";
  } else {
    fabLabel.textContent = "ساعدني أختار";
  }
}

// Public API
window.AdvisorWizard = {
  init,
  startFlow,
  reset: handleRestart,
  showResult,
  reopenWizardAtField,
  updateGlobalCTA,
  showToast
};

// Auto init when DOM ready
if(document.readyState==="loading"){
  document.addEventListener("DOMContentLoaded", init, {once:true});
} else {
  init();
}

})();

