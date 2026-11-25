(function(root){
"use strict";
const STORAGE_KEY = "ezhalha_advisor_state_v2";
const STORAGE_CHAT_KEY = "ezhalha_advisor_chat_v2";
const RETENTION_MS = 24 * 60 * 60 * 1000;

function defaultState(){
  return {
    storeStatus: null, // none | new | existing | specific | unknown
    platform: null, // salla | zid | unknown | null
    businessType: "",
    storeNameStatus: null, // yes | no | idea | null
    hasLogo: null, // true | false | onlyLogo | null  (true = جاهزة, onlyLogo = شعار فقط, false = لا)
    hasIdentity: null, // true | false | null (derived)
    productsReady: null, // yes | partial | no | null
    productsCount: null, // <10 | 10-20 | 20-35 | more | unknown | null
    budgetPreference: null, // basic | pro | full | null
    needsFullSetup: null, // boolean | null
    // new store
    preparedItems: [], // array of strings : logo, products, payment, shipping, domain, design, none
    goal: null, // design | sell | full | unknown | null
    // existing
    issues: [], // array: design, home, mobile, banners, products, seo, speed, payment_shipping, tracking, full, unknown
    storeUrl: "",
    // specific
    requestedServices: [], // service ids
    otherServiceText: "",
    // computed
    recommendedPackage: null, // plus | professional | gold | custom | null
    wizardPath: null,
    wizardStepIndex: 0,
    wizardHistory: [], // stack of { stepId, answer }
    updatedAt: Date.now()
  };
}

function loadState(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    if(!raw) return defaultState();
    const parsed = JSON.parse(raw);
    if(!parsed || typeof parsed!=="object" || !Number.isFinite(parsed.updatedAt) || Date.now()-parsed.updatedAt>RETENTION_MS){
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(STORAGE_CHAT_KEY);
      return defaultState();
    }
    // merge with defaults to handle new fields
    const def = defaultState();
    return Object.assign(def, parsed);
  }catch(e){ return defaultState(); }
}

function saveState(state){
  try{
    state.updatedAt = Date.now();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    // dispatch event for sync wizard <-> chat
    if(typeof window !== "undefined"){
      window.dispatchEvent(new CustomEvent("advisor:stateChanged", { detail: { state: clone(state) } }));
    }
  }catch(e){}
}

function clone(o){ return JSON.parse(JSON.stringify(o)); }

function resetState(){
  const s = defaultState();
  saveState(s);
  // also clear chat
  try{ localStorage.removeItem(STORAGE_CHAT_KEY); }catch(e){}
  if(typeof window !== "undefined"){
    window.dispatchEvent(new CustomEvent("advisor:reset"));
  }
  return s;
}

function updateState(patch){
  const s = loadState();
  Object.assign(s, patch);
  saveState(s);
  return s;
}

function mergeExtracted(extracted){
  if(!extracted || typeof extracted !== "object") return loadState();
  const allowed = {
    storeStatus: ["none","new","existing","specific","unknown"],
    platform: ["salla","zid","unknown",null],
    businessType: "string",
    storeNameStatus: ["yes","no","idea",null],
    hasLogo: [true,false,"onlyLogo","idea",null],
    hasIdentity: [true,false,null],
    productsReady: ["yes","partial","no",null],
    productsCount: ["<10","10-20","20-35","more","unknown",null],
    budgetPreference: ["basic","pro","full",null],
    needsFullSetup: [true,false,null],
    goal: ["design","sell","full","unknown",null],
    storeUrl: "string",
    needsDesign: "bool",
    needsSeo: "bool"
  };
  const s = loadState();
  let changed = false;
  for(const k in extracted){
    if(!(k in allowed)) continue;
    let v = extracted[k];
    // normalize booleans that come as string
    if(k==="hasLogo" && v==="true") v=true;
    if(k==="hasLogo" && v==="false") v=false;
    if(k==="needsFullSetup" && typeof v==="string") v = v==="true";
    const rule = allowed[k];
    if(Array.isArray(rule)){
      if(rule.includes(v) || v===null){
        if(s[k] !== v && v !== null && v !== undefined && v !== ""){
          s[k]=v; changed=true;
        } else if(v===null && s[k]===null){
          // no change
        }
      }
    } else if(rule==="string"){
      if(typeof v==="string" && v.trim() && s[k] !== v.trim()){
        s[k]=v.trim().slice(0,120); changed=true;
      }
    } else if(rule==="bool"){
      if(typeof v==="boolean" && s[k]!==v){ s[k]=v; changed=true; }
    }
  }
  // special handling for arrays like requestedServices, issues, preparedItems if provided
  if(Array.isArray(extracted.requestedServices)){
    const validIds = (root.ADVISOR_SERVICES||[]).map(x=>x.id);
    const filtered = extracted.requestedServices.filter(id=> validIds.includes(id));
    if(filtered.length && JSON.stringify(s.requestedServices)!==JSON.stringify(filtered)){
      s.requestedServices = filtered; changed=true;
    }
  }
  if(Array.isArray(extracted.issues)){
    const valid = ["design","home","mobile","banners","products","seo","speed","payment_shipping","tracking","full","unknown"];
    const filtered = extracted.issues.filter(x=> valid.includes(x));
    if(filtered.length && JSON.stringify(s.issues)!==JSON.stringify(filtered)){ s.issues=filtered; changed=true; }
  }
  if(Array.isArray(extracted.preparedItems)){
    const valid = ["logo","products","payment","shipping","domain","design","none"];
    const filtered = extracted.preparedItems.filter(x=> valid.includes(x));
    if(filtered.length && JSON.stringify(s.preparedItems)!==JSON.stringify(filtered)){ s.preparedItems=filtered; changed=true; }
  }
  if(extracted.businessType && typeof extracted.businessType==="string"){
    const bt = extracted.businessType.trim().slice(0,80);
    if(bt && s.businessType!==bt){ s.businessType=bt; changed=true; }
  }
  if(extracted.storeUrl && typeof extracted.storeUrl==="string"){
    const url = extracted.storeUrl.trim().slice(0,300);
    if(url && s.storeUrl!==url){ s.storeUrl=url; changed=true; }
  }
  if(changed) saveState(s);
  return s;
}

// Chat persistence helpers
function loadChat(){
  try{
    const raw = localStorage.getItem(STORAGE_CHAT_KEY);
    if(!raw) return [];
    const messages=JSON.parse(raw);
    if(!Array.isArray(messages)) return [];
    const recent=messages.filter(m=>m && typeof m.content==="string" && Number.isFinite(m.ts) && Date.now()-m.ts<RETENTION_MS);
    if(recent.length!==messages.length) saveChat(recent);
    return recent;
  }catch(e){ return []; }
}
function saveChat(messages){
  try{ localStorage.setItem(STORAGE_CHAT_KEY, JSON.stringify(messages.slice(-40))); }catch(e){}
}
function appendChatMessage(role, content, meta){
  const msgs = loadChat();
  msgs.push({ role, content, meta: meta||null, ts: Date.now() });
  saveChat(msgs);
  return msgs;
}
function clearChat(){
  try{ localStorage.removeItem(STORAGE_CHAT_KEY);}catch(e){}
}

const AdvisorState = {
  STORAGE_KEY,
  STORAGE_CHAT_KEY,
  defaultState,
  loadState,
  saveState,
  resetState,
  updateState,
  mergeExtracted,
  loadChat,
  saveChat,
  appendChatMessage,
  clearChat,
  clone
};

if(typeof module !== "undefined" && module.exports) module.exports = AdvisorState;
if(root) root.AdvisorState = AdvisorState;
})(typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : this);
