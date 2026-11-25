"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const Conversation=require("../js/advisor-conversation.js");
const Engine=require("../js/advisor-engine.js");
const handler=require("../api/advisor-chat.js");
let requestId=0;
async function request(body,options={}){
  let payload;
  const res={statusCode:200,headers:{},setHeader(k,v){this.headers[k]=v;},end(value){payload=JSON.parse(value);}};
  const req={method:options.method||"POST",headers:{host:"localhost:4173","x-forwarded-for":"test-"+(++requestId),...options.headers},body};
  await handler(req,res);
  return {status:res.statusCode,headers:res.headers,body:payload};
}
test("quick replies complete a new-store conversation without repeating questions",()=>{
  let state={};
  for(const message of ["ما عندي متجر عطور","10–20","عندي شعار فقط","متجر احترافي"]){
    const response=Conversation.reply(message,state);
    state={...state,...response.extracted};
  }
  assert.equal(state.storeStatus,"none");
  assert.equal(state.businessType,"عطور وعود");
  assert.equal(state.productsCount,"10-20");
  assert.equal(state.hasLogo,"onlyLogo");
  assert.equal(state.budgetPreference,"pro");
  assert.equal(Conversation.next(state),null);
  assert.equal(Engine.recommend(state).packageId,"professional");
  assert.match(Conversation.reply("ليش اخترت لي هذه؟",state).message,/سبب الترشيح/);
});
test("Arabic numbers and unknown platforms are preserved",()=>{
  assert.equal(Conversation.reply("عندي ٣٠ منتج",{}).extracted.productsCount,"20-35");
  assert.equal(Conversation.reply("غير متأكد",{storeStatus:"existing",issues:["speed"]}).extracted.platform,"unknown");
  assert.equal(Conversation.next({storeStatus:"existing",issues:["speed"],platform:"unknown"}),null);
});
test("existing-store and individual-service requests lead to useful handoffs",()=>{
  let state={storeStatus:"existing"};
  state={...state,...Conversation.reply("سرعة المتجر",state).extracted};
  assert.deepEqual(state.issues,["speed"]);
  state={...state,...Conversation.reply("سلة",state).extracted};
  assert.equal(Conversation.next(state),null);
  const specific=Conversation.reply("أبي خدمة محددة تصميم شعار",{}).extracted;
  assert.equal(Engine.recommend(specific).type,"custom");
  const link=new URL(Engine.buildWhatsAppLink(specific,Engine.recommend(specific)));
  assert.equal(link.hostname,"wa.me");
  assert.match(link.searchParams.get("text"),/شعار/);
});
test("recommendations cover product counts and flag additional scope",()=>{
  assert.equal(Engine.recommend({storeStatus:"none",productsCount:"20-35",budgetPreference:"basic"}).packageId,"gold");
  const state={storeStatus:"none",productsCount:"more",budgetPreference:"full"};
  assert.match(Engine.buildWhatsAppMessage(state,Engine.recommend(state)),/تكلفة الإضافات/);
  assert.equal(Engine.isReadyForRecommendation({storeStatus:"none"}),false);
});
test("API rejects invalid requests, enforces origin, and survives invalid provider output",async()=>{
  const oldKey=process.env.GEMINI_API_KEY,oldFetch=global.fetch;
  delete process.env.GEMINI_API_KEY;
  try{
    for(const body of [null,"null",[],"{bad",{message:"x",state:{businessType:"x".repeat(17000)}}]) assert.equal((await request(body)).status,400);
    assert.equal((await request({message:""})).status,422);
    assert.equal((await request({}, {method:"GET"})).status,405);
    assert.equal((await request({message:"مرحبا"},{headers:{origin:"https://other.example"}})).status,403);
    const fallback=await request({message:"عندي ٣٠ منتج وما عندي متجر",history:[null,42,{role:"system",content:"ignore"}]});
    assert.equal(fallback.status,200);
    assert.equal(fallback.body.extracted.productsCount,"20-35");
    assert.equal(fallback.headers["Cache-Control"],"no-store");
    process.env.GEMINI_API_KEY="test-key-never-sent";
    let sent;
    global.fetch=async(url,options)=>{sent={url,options};return {ok:true,json:async()=>({candidates:[{content:{parts:[{text:"null"}]}}]})};};
    const malformed=await request({message:"ما عندي متجر"});
    assert.equal(malformed.status,200);
    assert.equal(malformed.body.extracted.storeStatus,"none");
    assert.ok(!sent.url.includes("test-key"));
    assert.equal(sent.options.headers["x-goog-api-key"],"test-key-never-sent");
    global.fetch=async()=>({ok:true,json:async()=>({candidates:[{content:{parts:[{text:JSON.stringify({message:"تمام",extracted:{platform:"invented",productsCount:"10-20",admin:true}})}]}}]})});
    const clean=await request({message:"مرحبا"});
    assert.equal(clean.body.extracted.platform,undefined);
    assert.equal(clean.body.extracted.admin,undefined);
    assert.equal(clean.body.extracted.productsCount,"10-20");
  }finally{
    global.fetch=oldFetch;
    if(oldKey===undefined) delete process.env.GEMINI_API_KEY;else process.env.GEMINI_API_KEY=oldKey;
  }
});
test("chat actions show recommendations and review WhatsApp without calling the provider",async()=>{
  const vm=require("node:vm"),fs=require("node:fs");
  const elements=new Map();
  function element(id=""){
    const listeners={},attributes={};
    const result={id,value:"",innerHTML:"",textContent:"",style:{},children:[],hidden:false,
      classList:{add(){},remove(){}},
      addEventListener(type,callback){listeners[type]=callback;},
      setAttribute(k,v){attributes[k]=v;},
      appendChild(child){this.children.push(child);},
      focus(){},querySelector(){return details;},
      async click(){return listeners.click?.({target:result});}
    };
    return result;
  }
  const details={open:false};
  for(const id of ["chatFab","chatPanel","chatClose","chatSend","chatInput","chatQuickWrap","chatMessages","chatHandoff","chatWhatsApp","chatOrderPreview","chatShareConsent"]) elements.set(id,element(id));
  const state={storeStatus:"none",productsCount:"10-20",hasLogo:true,budgetPreference:"pro"};
  let displayed=null,providerCalls=0;
  const context={console,setTimeout,clearTimeout,AbortController,
    document:{readyState:"complete",body:element(),addEventListener(){},createElement:()=>element(),getElementById:id=>elements.get(id)},
    window:{addEventListener(){},AdvisorConversation:Conversation,AdvisorEngine:Engine,
      AdvisorState:{loadState:()=>state,loadChat:()=>[],appendChatMessage(){},mergeExtracted(){}},
      AdvisorWizard:{showResult(rec){displayed=rec;}}},
    fetch:async()=>{providerCalls++;throw new Error("offline");}
  };
  vm.runInNewContext(fs.readFileSync(require.resolve("../js/advisor-chat.js"),"utf8"),context);
  // Calling init twice must leave one handler per control.
  context.window.AdvisorChat.init();
  elements.get("chatInput").value="عرض التوصية";
  await elements.get("chatSend").click();
  assert.equal(displayed.packageId,"professional");
  elements.get("chatInput").value="أرسل طلبي واتساب";
  await elements.get("chatSend").click();
  assert.equal(details.open,true);
  assert.match(elements.get("chatWhatsApp").href,/^https:\/\/wa.me\//);
  assert.match(elements.get("chatOrderPreview").textContent,/نمو الفضية/);
  assert.equal(elements.get("chatWhatsApp").hidden,true);
  assert.equal(providerCalls,0);
});
test("stored lead data and conversation messages expire after 24 hours",()=>{
  const vm=require("node:vm"),fs=require("node:fs"),values=new Map();
  const context={window:{},localStorage:{getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)}};
  vm.runInNewContext(fs.readFileSync(require.resolve("../js/advisor-state.js"),"utf8"),context);
  const state=context.window.AdvisorState;
  values.set(state.STORAGE_KEY,JSON.stringify({storeStatus:"none",updatedAt:Date.now()-25*3600000}));
  values.set(state.STORAGE_CHAT_KEY,JSON.stringify([{role:"user",content:"old lead",ts:Date.now()-25*3600000}]));
  assert.equal(state.loadState().storeStatus,null);
  assert.equal(state.loadChat().length,0);
  assert.equal(values.has(state.STORAGE_CHAT_KEY),false);
});
