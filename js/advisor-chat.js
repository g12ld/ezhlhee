(function(){
"use strict";
const State = window.AdvisorState;
const Engine = window.AdvisorEngine;
const PACKAGES = window.ADVISOR_PACKAGES;
const SERVICES = window.ADVISOR_SERVICES;

let chatOpen = false;
let sending = false;
let initialized = false;
let lastRecommendation = "";
let chatRevision = 0;
let activeRequest = null;

function el(id){ return document.getElementById(id); }
function escapeHtml(s){ return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }

function initChat(){
  if(initialized) return;
  initialized = true;
  document.addEventListener("keydown", function(e){
    if(e.key === "Escape" && chatOpen){ closeChat(); el("chatFab")?.focus(); }
  });
  window.addEventListener("advisor:reset", function(){ lastRecommendation=""; updateHandoff(); });
  window.addEventListener("advisor:stateChanged", updateHandoff);
  updateHandoff();
  const fab = el("chatFab");
  const panel = el("chatPanel");
  const closeBtn = el("chatClose");
  const sendBtn = el("chatSend");
  const input = el("chatInput");
  const quickWrap = el("chatQuickWrap");

  if(fab) fab.addEventListener("click", toggleChat);
  if(closeBtn) closeBtn.addEventListener("click", closeChat);
  const shareConsent=el("chatShareConsent");
  if(shareConsent) shareConsent.addEventListener("change",function(){
    const link=el("chatWhatsApp");
    if(link) link.hidden=!shareConsent.checked;
  });
  if(sendBtn) sendBtn.addEventListener("click", handleSend);
  if(input){
    input.addEventListener("keydown", function(e){
      if(e.key==="Enter" && !e.shiftKey && !e.isComposing){ e.preventDefault(); handleSend(); }
    });
  }
  // delegate suggestion clicks
  if(quickWrap){
    quickWrap.addEventListener("click", function(e){
      const btn = e.target.closest(".chat-suggestion");
      if(btn){
        const val = btn.dataset.value || btn.textContent.trim();
        if(input) input.value = val;
        handleSend();
      }
    });
  }
  const msgsEl = el("chatMessages");
  if(msgsEl){
    msgsEl.addEventListener("click", function(e){
      const btn = e.target.closest(".chat-suggestion");
      if(btn && btn.dataset.value){
        // bubble suggestions
        const val = btn.dataset.value;
        const input = el("chatInput");
        if(input) input.value = val;
        handleSend();
      }
    });
  }
  // click outside to close on mobile? keep simple
  document.addEventListener("click", function(e){
    const panel = el("chatPanel");
    const fab = el("chatFab");
    if(!panel || !fab) return;
    if(chatOpen && !panel.contains(e.target) && !fab.contains(e.target)){
      // don't auto close on desktop, only if mobile?
      // keep open
    }
  });
  // load history
  renderHistory();
  // listen to state change to update quick replies visibility
  window.addEventListener("advisor:stateChanged", function(){
    // could update placeholder
  });
}

function toggleChat(){
  if(chatOpen) closeChat(); else openChat();
}
function openChat(){
  const panel = el("chatPanel");
  const fab = el("chatFab");
  if(!panel) return;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden","false");
  chatOpen = true;
  if(fab) fab.setAttribute("aria-expanded","true");
  // focus input
  const input = el("chatInput");
  if(input) setTimeout(()=> input.focus(), 280);
  // if first time, show welcome if no messages
  const msgs = State.loadChat();
  if(!msgs.length){
    const state = State.loadState();
    const welcome = buildWelcome(state);
    appendAssistant(welcome.text, { suggestions: welcome.suggestions });
  }
  // mark fab as opened
  document.body.classList.add("chat-open");
}
function closeChat(){
  const panel = el("chatPanel");
  const fab = el("chatFab");
  if(!panel) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden","true");
  chatOpen=false;
  if(fab) fab.setAttribute("aria-expanded","false");
  document.body.classList.remove("chat-open");
}

function buildWelcome(state){
  // If state already has some data, acknowledge
  if(state.storeStatus){
    return {
      text: `أهلًا 👋\nأنا مساعد إزهلها. شفت أنك بدأت تحدد احتياجك — خلنا نكمل سوا.\n\nوش حاب تسأل عنه الآن؟`,
      suggestions: ["كم تكلفة الباقة؟","ليش اخترت لي هذه؟","أبي أغير إجابتي","أرسل طلبي واتساب"]
    };
  }
  return {
    text: `أهلًا 👋\nأنا مساعد إزهلها.\nما تحتاج تعرف أسماء الخدمات أو الباقات.\nقل لي وش عندك حاليًا وش تبي توصل له، وأنا أرتب لك احتياجك.`,
    suggestions: ["ما عندي متجر","عندي متجر","أبي أطور متجري","أبي أعرف الأسعار","مو عارف وش أحتاج"]
  };
}

function renderHistory(){
  const msgs = State.loadChat();
  const container = el("chatMessages");
  if(!container) return;
  container.innerHTML="";
  msgs.forEach(m=>{
    if(m.role==="user") renderBubble("user", m.content);
    else if(m.role==="assistant") renderBubble("assistant", m.content, m.meta);
    else if(m.role==="system") renderBubble("system", m.content);
  });
  scrollToBottom();
  // also render suggestions for last assistant if any
  const last = msgs[msgs.length-1];
  if(last && last.role==="assistant" && last.meta && last.meta.suggestions){
    renderQuickReplies(last.meta.suggestions);
  }
}

function renderBubble(role, text, meta){
  const container = el("chatMessages");
  if(!container) return;
  const div = document.createElement("div");
  div.className = "chat-bubble " + role;
  // simple markdown for line breaks
  const html = escapeHtml(text).replace(/\n/g,"<br>");
  div.innerHTML = html;
  // if assistant meta has suggestions as buttons inside bubble? we keep separate
  container.appendChild(div);
  // if bubble is assistant and has quick suggestions inside meta, also show chips below bubble
  // handled via renderQuickReplies
}

function renderQuickReplies(suggestions){
  const wrap = el("chatQuickWrap");
  if(!wrap) return;
  wrap.innerHTML="";
  if(!suggestions || !suggestions.length){
    wrap.style.display="none";
    return;
  }
  wrap.style.display="flex";
  suggestions.slice(0,5).forEach(s=>{
    const btn = document.createElement("button");
    btn.type="button";
    btn.className="chat-suggestion";
    btn.textContent = s;
    btn.dataset.value = s;
    wrap.appendChild(btn);
  });
}

function appendUser(text){
  State.appendChatMessage("user", text);
  renderBubble("user", text);
  scrollToBottom();
}
function appendAssistant(text, meta){
  State.appendChatMessage("assistant", text, meta);
  renderBubble("assistant", text, meta);
  if(meta && meta.suggestions) renderQuickReplies(meta.suggestions);
  else {
    const wrap = el("chatQuickWrap");
    if(wrap) wrap.style.display="none";
  }
  scrollToBottom();
}
function appendSystem(text){
  State.appendChatMessage("system", text);
  renderBubble("system", text);
  scrollToBottom();
}
function showTyping(){
  const container = el("chatMessages");
  if(!container) return null;
  const div = document.createElement("div");
  div.className="chat-bubble assistant";
  div.id="chatTyping";
  div.innerHTML='<div class="chat-typing"><span></span><span></span><span></span></div>';
  container.appendChild(div);
  scrollToBottom();
  return div;
}
function hideTyping(){
  const t = el("chatTyping");
  if(t) t.remove();
}
function scrollToBottom(){
  const c = el("chatMessages");
  if(c) c.scrollTop = c.scrollHeight;
}

async function handleSend(){
  if(sending) return;
  const input = el("chatInput");
  if(!input) return;
  const text = (input.value||"").trim();
  if(!text) return;
  input.value="";
  if(handleAction(text)) return;
  appendUser(text);
  // clear quick replies
  const wrap = el("chatQuickWrap");
  if(wrap) wrap.style.display="none";

  sending=true;
  const revision=chatRevision;
  const sendBtn = el("chatSend");
  if(sendBtn) sendBtn.disabled=true;
  showTyping();
  el("chatMessages")?.setAttribute("aria-busy","true");

  try{
    const state = State.loadState();
    const history = State.loadChat().slice(-10).map(m=> ({role:m.role, content:m.content}));
    const response = await callAdvisorAPI(text, state, history);
    if(revision!==chatRevision) return;
    hideTyping();
    if(response){
      // Merge extracted
      if(response.extracted) State.mergeExtracted(response.extracted);
      const newState = State.loadState();
      // Determine message to show
      const msg = response.message || response.nextQuestion || "تمام، خلنا نكمل.";
      const suggestions = response.suggestions || [];
      appendAssistant(msg, {suggestions});
      updateHandoff();
      const rec = Engine.recommend(newState);
      if(rec && !window.AdvisorConversation.next(newState)){
        const signature = JSON.stringify([rec.packageId, newState.productsCount, newState.requestedServices]);
        if(signature !== lastRecommendation){
          lastRecommendation=signature;
          const name = rec.type === "custom" ? "خدمة مخصصة" : rec.package.fullName;
          appendAssistant("الترشيح المبدئي: " + name + ". راجع التفاصيل والملخص قبل التواصل.", {suggestions:["عرض التوصية","أرسل طلبي واتساب","أبدأ من جديد"]});
        }
        window.AdvisorWizard?.updateGlobalCTA(rec);
      }
    } else {
      hideTyping();
      appendAssistant("صار فيه خلل بسيط في الاتصال. لكن أقدر أكمل معك بدون AI — قل لي كم منتج عندك أو وش وضع متجرك؟", {suggestions:["أقل من 10","10–20","20–35","أكثر","ما عندي متجر"]});
    }
  } catch(e){
    hideTyping();
    appendAssistant("الشبكة بطيئة الآن — بجاوبك بطريقة مبسطة: قل لي وش وضع متجرك الحالي؟", {suggestions:["ما عندي متجر","عندي متجر جديد","أبي أطور متجري","أبي خدمة محددة"]});
  } finally {
    el("chatMessages")?.setAttribute("aria-busy","false");
    sending=false;
    if(sendBtn) sendBtn.disabled=false;
    const input2 = el("chatInput");
    if(input2 && chatOpen) input2.focus();
  }
}

async function callAdvisorAPI(message, state, history){
  const controller = new AbortController();
  activeRequest=controller;
  const timer = setTimeout(()=>controller.abort(), 12000);
  try{
    const res = await fetch("/api/advisor-chat", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message,state,history}), signal:controller.signal
    });
    if(!res.ok) throw new Error("api_error");
    const data = await res.json();
    if(!data || !data.ok || typeof data.message!=="string") throw new Error("invalid_response");
    return data;
  }catch{
    return localAdvisorFallback(message,state);
  }finally{ clearTimeout(timer); if(activeRequest===controller) activeRequest=null; }
}

function updateHandoff(){
  const state=State.loadState();
  const handoff=el("chatHandoff");
  if(!handoff) return;
  const ready=!!state.storeStatus && state.storeStatus!=="unknown";
  handoff.hidden=!ready;
  if(!ready) return;
  const rec=window.AdvisorConversation.next(state) ? null : Engine.recommend(state);
  el("chatOrderPreview").textContent=Engine.buildWhatsAppMessage(state,rec);
  el("chatWhatsApp").href=Engine.buildWhatsAppLink(state,rec);
  const consent=el("chatShareConsent");
  if(consent){consent.checked=false;el("chatWhatsApp").hidden=true;}
}

function handleAction(text){
  const value=window.AdvisorConversation.normalize(text);
  if(/واتس/.test(value)){
    updateHandoff();
    const state=State.loadState();
    if(!state.storeStatus || state.storeStatus==="unknown"){
      appendAssistant("حدد وضع متجرك أولًا عشان أجهز لك ملخصًا مفيدًا.", {suggestions:["ما عندي متجر","عندي متجر","أبي خدمة محددة"]});
    }else{
      appendAssistant("ملخصك جاهز أسفل المحادثة. راجعه ثم اضغط «افتح واتساب بالملخص»؛ الإرسال يتم من داخل واتساب.");
      el("chatHandoff").querySelector("details").open=true;
      (el("chatShareConsent") || el("chatWhatsApp")).focus();
    }
    return true;
  }
  if(value==="عرض التوصية"){
    const state=State.loadState(), step=window.AdvisorConversation.next(state);
    if(step) appendAssistant(step.question,{suggestions:step.suggestions});
    else{
      const rec=Engine.recommend(state);
      if(rec){ window.AdvisorWizard?.showResult(rec,state); closeChat(); }
    }
    return true;
  }
  if(/ابدا من جديد|غير اجابتي|اغير اجابتي/.test(value)){
    window.AdvisorWizard?.reset();
    return true;
  }
  return false;
}

function localAdvisorFallback(message, state){
  return window.AdvisorConversation.reply(message, state);
}

// Public: called from result box
function askFromResult(question, state, rec){
  openChat();
  const input = el("chatInput");
  if(input) input.value = question;
  handleSend();
  // Also append context answer in result area after response?
  // The chat will handle it
}

// For clearing chat UI after reset
function clearUI(){
  chatRevision++;
  activeRequest?.abort();
  lastRecommendation="";
  State.clearChat();
  const container = el("chatMessages");
  if(container) container.innerHTML="";
  const wrap = el("chatQuickWrap");
  if(wrap) wrap.innerHTML="", wrap.style.display="none";
  // show welcome again
  setTimeout(()=>{
    const state = State.loadState();
    const w = buildWelcome(state);
    appendAssistant(w.text, {suggestions: w.suggestions});
  }, 300);
}

// Expose
window.AdvisorChat = {
  init: initChat,
  open: openChat,
  close: closeChat,
  toggle: toggleChat,
  askFromResult,
  clearUI
};

if(document.readyState==="loading"){
  document.addEventListener("DOMContentLoaded", initChat, {once:true});
} else {
  initChat();
}
})();

