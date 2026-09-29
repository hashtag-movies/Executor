"""Hashtag Console UI V3. Fixed shell, persistent permission status flow, improved send control."""

CONSOLE_HTML = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hashtag Console</title><style>:root{color-scheme:dark;--bg:#050812;--panel:#09111f;--panel2:#0c1627;--muted:#8292ad;--text:#edf4ff;--accent:#78a9ff;--good:#58dda0;--gold:#f2c76d;--danger:#ef7784}*{box-sizing:border-box}html,body{width:100%;height:100%;margin:0;overflow:hidden}body{background:radial-gradient(circle at 20% -10%,#14213a 0,#050812 42%),#050812;color:var(--text);font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}.app{position:fixed;inset:0;display:grid;grid-template-columns:minmax(0,1fr) 320px;overflow:hidden}.chat{min-width:0;min-height:0;display:grid;grid-template-rows:72px minmax(0,1fr) auto;overflow:hidden}.top{height:72px;min-height:72px;border-bottom:1px solid rgba(120,169,255,.14);padding:0 24px;display:flex;align-items:center;justify-content:space-between;background:rgba(5,8,18,.94);backdrop-filter:blur(18px);position:relative;z-index:5}.brand{font-size:18px;font-weight:850;letter-spacing:-.02em}.sub{font-size:11px;color:var(--muted);font-weight:550;margin-top:2px}.status{display:flex;align-items:center;gap:7px;font-size:12px;color:#9fb0c8;padding:7px 12px;border:1px solid rgba(120,169,255,.16);border-radius:999px;background:rgba(14,23,40,.78)}.status-dot{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 12px rgba(88,221,160,.7);animation:statusPulse 1.8s ease-in-out infinite}.messages{min-height:0;overflow-y:auto;overflow-x:hidden;padding:30px 28px;scroll-behavior:smooth}.empty{text-align:center;max-width:700px;margin:15vh auto;animation:rise .6s ease both}.empty h1{font-size:clamp(34px,5vw,54px);margin:0 0 12px;letter-spacing:-.045em;background:linear-gradient(110deg,#fff,#91b9ff);-webkit-background-clip:text;background-clip:text;color:transparent}.empty p{color:var(--muted);line-height:1.7}.msg{max-width:900px;margin:0 auto 18px;display:flex;gap:10px;animation:msgIn .32s cubic-bezier(.2,.8,.2,1) both}.msg.user{justify-content:flex-end}.avatar{width:34px;height:34px;flex:0 0 34px;border-radius:11px;background:linear-gradient(145deg,#14233d,#0b1425);border:1px solid rgba(120,169,255,.18);display:grid;place-items:center;color:var(--accent);font-weight:850;box-shadow:0 8px 28px rgba(0,0,0,.22)}.bubble{max-width:780px;background:rgba(13,20,34,.92);border:1px solid rgba(120,169,255,.13);border-radius:18px;padding:13px 16px;white-space:pre-wrap;line-height:1.58;overflow-wrap:anywhere;box-shadow:0 10px 32px rgba(0,0,0,.14);backdrop-filter:blur(12px)}.user .bubble{background:linear-gradient(145deg,#172844,#122039);border-color:rgba(120,169,255,.25)}.assistant-flow{width:min(780px,100%)}.flow-bubble{max-width:none}.flow-head{display:flex;align-items:center;gap:9px;color:#b8c8dd}.flow-icon{width:8px;height:8px;border-radius:50%;background:#78a9ff;box-shadow:0 0 12px rgba(120,169,255,.65)}.flow-text{line-height:1.55}.flow-status{margin-top:9px;color:#7f92ae;font-size:11px;display:flex;align-items:center;gap:7px}.flow-status.done{color:#83d9ae}.flow-status.error{color:#f29ca5}.mini-dots{display:inline-flex;gap:4px}.mini-dots i{width:5px;height:5px;border-radius:50%;background:#78a9ff;animation:dot 1.05s infinite}.mini-dots i:nth-child(2){animation-delay:.14s}.mini-dots i:nth-child(3){animation-delay:.28s}.result-message .bubble{min-width:min(660px,78vw);padding:0;overflow:hidden;border-color:rgba(120,169,255,.18);background:linear-gradient(145deg,rgba(12,20,34,.98),rgba(9,17,29,.98));box-shadow:0 14px 45px rgba(0,0,0,.24)}.result-head{display:flex;align-items:center;gap:9px;padding:11px 15px;border-bottom:1px solid rgba(120,169,255,.12);font-size:11px;color:#9db4c4;text-transform:uppercase;letter-spacing:.09em}.result-symbol{width:24px;height:24px;border-radius:8px;display:grid;place-items:center;background:rgba(120,169,255,.1);border:1px solid rgba(120,169,255,.16);color:#9ec0ff;font-size:12px}.result-body{padding:15px 16px;font-size:14px;color:#edf4ff;white-space:pre-wrap}.thinking .bubble{color:#9db0ca;display:flex;align-items:center;gap:9px}.dots{display:inline-flex;gap:4px}.dots i{width:5px;height:5px;border-radius:50%;background:#7ea9f5;animation:dot 1.1s infinite}.dots i:nth-child(2){animation-delay:.14s}.dots i:nth-child(3){animation-delay:.28s}.composer{padding:14px 28px 18px;background:linear-gradient(transparent,rgba(5,8,18,.94) 18%,#050812 55%);z-index:10}.box{max-width:900px;margin:auto;background:rgba(11,18,32,.94);border:1px solid rgba(120,169,255,.2);border-radius:20px;padding:10px;box-shadow:0 16px 50px rgba(0,0,0,.3);backdrop-filter:blur(18px)}.box:focus-within{border-color:rgba(120,169,255,.42);box-shadow:0 16px 55px rgba(0,0,0,.34),0 0 34px rgba(120,169,255,.07)}textarea{width:100%;min-height:52px;max-height:170px;resize:none;border:0;outline:0;background:transparent;color:var(--text);padding:9px 10px;font:inherit}.actions{display:flex;justify-content:space-between;align-items:center;padding:2px 3px 0 9px}.hint{font-size:11px;color:#62738e}.send{background:linear-gradient(135deg,#79aaff,#5e8ee7);color:#06101e;border:0;border-radius:11px;padding:9px 17px;font-weight:850;cursor:pointer;box-shadow:0 7px 22px rgba(90,140,230,.18);transition:transform .18s,filter .18s}.send:hover{transform:translateY(-1px);filter:brightness(1.08)}.send:disabled{opacity:.55;cursor:wait}.side{min-width:0;min-height:0;border-left:1px solid rgba(120,169,255,.13);background:rgba(7,12,22,.94);padding:18px;overflow-y:auto;overflow-x:hidden;backdrop-filter:blur(18px)}.side h3{font-size:11px;text-transform:uppercase;letter-spacing:.11em;color:#91a2bd;margin:11px 2px}.card{background:rgba(13,20,34,.84);border:1px solid rgba(120,169,255,.12);border-radius:14px;padding:13px;margin-bottom:13px;font-size:12px;box-shadow:0 8px 26px rgba(0,0,0,.12)}.permission-card{padding:14px;border-color:rgba(242,199,109,.24);background:linear-gradient(145deg,rgba(34,28,17,.68),rgba(13,20,34,.9));animation:permIn .3s ease both}.permission-title{display:flex;align-items:center;gap:9px;font-weight:800;color:#f3d38d}.permission-icon{width:27px;height:27px;border-radius:9px;display:grid;place-items:center;background:rgba(242,199,109,.1);border:1px solid rgba(242,199,109,.18);color:#f2c76d}.permission-meta{margin-top:11px;color:#9eacc0;line-height:1.55}.permission-resource{margin-top:8px;padding:8px 9px;border-radius:9px;background:rgba(0,0,0,.18);border:1px solid rgba(255,255,255,.05);color:#d5dfec;word-break:break-word;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:10px}.permission-actions{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:11px}.permission-actions button{border:0;border-radius:9px;padding:8px 9px;font-size:10px;font-weight:800;cursor:pointer;transition:transform .15s,filter .15s}.permission-actions button:hover{transform:translateY(-1px);filter:brightness(1.08)}.allow{background:#55d88a;color:#06140d}.task{background:#6ea8ff;color:#07101e}.deny{grid-column:1/-1;background:rgba(239,107,120,.12);border:1px solid rgba(239,107,120,.2)!important;color:#f49aa4}.permission-note{margin-top:9px;color:#697b96;font-size:10px;line-height:1.45}.status-error{color:#f29ca5}pre{white-space:pre-wrap;overflow:auto;max-height:260px;font-size:10px;color:#b9c9df}@keyframes msgIn{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:none}}@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}@keyframes statusPulse{50%{opacity:.62;box-shadow:0 0 7px rgba(88,221,160,.4)}}@keyframes dot{0%,70%,100%{opacity:.25;transform:translateY(0)}35%{opacity:1;transform:translateY(-3px)}}@keyframes permIn{from{opacity:0;transform:translateX(8px)}to{opacity:1;transform:none}}@media(max-width:850px){.app{grid-template-columns:1fr}.side{display:none}.messages{padding-left:16px;padding-right:16px}.result-message .bubble{min-width:0;max-width:88vw}}
.send{min-width:112px;height:42px;display:inline-flex;align-items:center;justify-content:center;gap:9px;position:relative;overflow:hidden;background:linear-gradient(135deg,#86b5ff 0%,#5d8eea 55%,#6e9ff7 100%);color:#06101e;border:1px solid rgba(255,255,255,.2);border-radius:13px;padding:0 18px;font-size:12px;font-weight:900;letter-spacing:.01em;cursor:pointer;box-shadow:0 9px 28px rgba(75,132,224,.25),inset 0 1px rgba(255,255,255,.3);transition:transform .18s ease,box-shadow .18s ease,filter .18s ease}.send:before{content:"";position:absolute;inset:-60% auto -60% -35%;width:35%;transform:skewX(-18deg);background:rgba(255,255,255,.24);filter:blur(4px);transition:left .45s ease}.send:hover{transform:translateY(-2px);filter:brightness(1.08);box-shadow:0 13px 34px rgba(75,132,224,.34),inset 0 1px rgba(255,255,255,.34)}.send:hover:before{left:110%}.send:active{transform:translateY(0) scale(.98)}.send:disabled{opacity:.58;cursor:wait;transform:none}.send-icon{width:16px;height:16px;display:grid;place-items:center;font-size:14px;transition:transform .18s ease}.send:hover .send-icon{transform:translateX(2px)}.send.busy .send-icon{animation:sendSpin 1s linear infinite}@keyframes sendSpin{to{transform:rotate(360deg)}}.flow-bubble{position:relative;overflow:hidden}.flow-bubble:after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:linear-gradient(90deg,transparent,#78a9ff,transparent);opacity:.35;animation:flowLine 2.2s linear infinite}.flow-status.done{color:#83d9ae}.flow-status.error{color:#f29ca5}.flow-status.approved{color:#a8c7fa}@keyframes flowLine{from{transform:translateX(-100%)}to{transform:translateX(100%)}}.side{overflow:hidden;display:flex;flex-direction:column}.side h3{flex:0 0 auto}.side .card{flex:0 0 auto}.side #permissions{max-height:245px;overflow:auto;padding-right:3px}.side #execution{min-height:0;flex:1;overflow:hidden}.side #execution pre{max-height:none;height:100%;margin:0;overflow:auto}.permission-card{max-height:230px;overflow:auto}.permission-actions button{min-height:34px}.permission-note{margin-bottom:2px}.result-symbol{font-weight:900}.flow-icon{background:#78a9ff}.msg-meta{font-size:10px;color:#788ea8;margin-top:6px;display:flex;align-items:center;gap:6px;font-weight:500}.user .msg-meta{justify-content:flex-end;color:#8fa4c3}.msg-meta .time-tag{display:inline-flex;align-items:center;gap:3px;background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:6px;border:1px solid rgba(255,255,255,0.06)}.msg-meta .duration-tag{display:inline-flex;align-items:center;gap:3px;background:rgba(120,169,255,0.1);color:#9ec0ff;padding:2px 6px;border-radius:6px;border:1px solid rgba(120,169,255,0.16)}</style></head><body><div class="app"><section class="chat"><div class="top"><div class="brand"># Hashtag Console<div class="sub">Core brain · Executor body</div></div><div id="status" class="status"><span class="status-dot"></span> Connecting…</div></div><div id="messages" class="messages"><div id="empty" class="empty"><h1>Talk to Hashtag.</h1><p>Type what you want in normal language. Hashtag Core plans the work and the Executor carries it out.</p></div></div><div class="composer"><div class="box"><textarea id="input" placeholder="Message Hashtag…"></textarea><div class="actions"><span class="hint">Enter to send · Shift+Enter for new line</span><button id="send" class="send"><span class="send-label">Send</span><span class="send-icon">➜</span></button></div></div></div></section><aside class="side"><h3>System</h3><div id="system" class="card">Loading…</div><h3>PC Local Drive</h3><div id="pc_drive" class="card">Checking PC Link…</div><h3>GitHub Web</h3><div id="github" class="card">Checking GitHub…</div><h3>Permissions</h3><div id="permissions"><div class="card">No pending requests.</div></div><h3>Last execution</h3><div id="execution" class="card">Nothing yet.</div></aside></div><script>

(function(){
"use strict";
var NL=String.fromCharCode(10);
var activeFlow=null;
var lastPendingIds={};

function $(id){return document.getElementById(id);}
function esc(value){
 var s=String(value===null||value===undefined?"":value);
 return s.replace(/[&<>"']/g,function(c){
  var m={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"};
  return m[c];
 });
}
function api(url,options){
 options=options||{};
 var headers=options.headers||{};
 headers["Content-Type"]="application/json";
 var fo={method:options.method||"GET",headers:headers};
 if(options.body!==undefined){fo.body=options.body;}
 return fetch(url,fo).then(function(response){
  return response.text().then(function(raw){
   var data={};
   try{data=raw?JSON.parse(raw):{};}catch(e){data={};}
   if(!response.ok){throw new Error(data.detail||data.error||("HTTP "+response.status));}
   return data;
  });
 });
}
function scrollMessages(){
 var box=$("messages");
 if(box){box.scrollTop=box.scrollHeight;}
}
function removeEmpty(){
 var e=$("empty");
 if(e&&e.parentNode){e.parentNode.removeChild(e);}
}
function formatClock(d){
 d=d||new Date();
 var h=d.getHours(),m=d.getMinutes(),ap=h>=12?"PM":"AM";
 h=h%12;h=h?h:12;m=m<10?"0"+m:m;
 return h+":"+m+" "+ap;
}
function addMessage(role,message,kind,meta){
 removeEmpty();
 var item=document.createElement("div");
 item.className="msg "+role+(kind?" "+kind:"");
 var metaHtml="";
 if(meta){
  if(meta.sentAt){
   metaHtml='<div class="msg-meta"><span class="time-tag">Sent '+esc(meta.sentAt)+'</span></div>';
  }else if(meta.duration){
   metaHtml='<div class="msg-meta"><span class="duration-tag">⏱ '+esc(meta.duration)+'</span><span class="time-tag">'+esc(meta.completedAt||formatClock())+'</span></div>';
  }
 }
 if(kind==="result"){
  item.innerHTML='<div class="avatar">#</div><div class="bubble"><div class="result-head"><span class="result-symbol">✓</span>Hashtag result</div><div class="result-body">'+esc(message)+'</div>'+metaHtml+'</div>';
 }else if(kind==="thinking"){
  item.className+=" thinking";
  item.innerHTML='<div class="avatar">#</div><div class="bubble">Hashtag is thinking <span class="dots"><i></i><i></i><i></i></span></div>';
 }else{
  item.innerHTML=role==="user"?'<div class="bubble">'+esc(message)+metaHtml+'</div>':'<div class="avatar">#</div><div class="bubble">'+esc(message)+metaHtml+'</div>';
 }
 $("messages").appendChild(item);
 scrollMessages();
 return item;
}
function addFlowMessage(){
 removeEmpty();
 if(activeFlow&&activeFlow.parentNode){activeFlow.parentNode.removeChild(activeFlow);}
 var item=document.createElement("div");
 item.className="msg assistant";
 item.innerHTML='<div class="avatar">#</div><div class="assistant-flow"><div class="bubble flow-bubble"><div class="flow-head"><span class="flow-icon"></span><span class="flow-text">Hashtag understood the request, but the Executor requires user permission before this operation can continue.</span></div><div class="flow-status status-busy">Waiting for your permission <span class="mini-dots"><i></i><i></i><i></i></span></div></div></div>';
 $("messages").appendChild(item);
 activeFlow=item;
 scrollMessages();
 return item;
}
function flowText(){
 return activeFlow?activeFlow.querySelector(".flow-text"):null;
}
function flowStatus(){
 return activeFlow?activeFlow.querySelector(".flow-status"):null;
}
function setFlowApproved(){
 if(!activeFlow){return;}
 var text=flowText(),status=flowStatus();
 if(text){text.textContent="Permission approved. Continuing...";}
 if(status){
  status.className="flow-status approved";
  status.innerHTML='Executing safely <span class="mini-dots"><i></i><i></i><i></i></span>';
 }
 scrollMessages();
}
function setFlowDone(){
 if(!activeFlow){return;}
 var text=flowText(),status=flowStatus();
 if(text){text.textContent="Done. Hashtag completed the request.";}
 if(status){
  status.className="flow-status done";
  status.textContent="Completed and verified";
 }
 scrollMessages();
}
function setFlowError(message){
 if(!activeFlow){addMessage("assistant",message);return;}
 var text=flowText(),status=flowStatus();
 if(text){text.textContent=message;}
 if(status){
  status.className="flow-status error";
  status.textContent="Execution stopped";
 }
 scrollMessages();
}
function executionResult(response){
 if(!response){return null;}
 if(response.execution&&response.execution.result!==undefined){return response.execution.result;}
 if(response.result&&response.result.execution&&response.result.execution.result!==undefined){return response.result.execution.result;}
 if(response.result&&response.result.result!==undefined){return response.result.result;}
 return null;
}
function resultText(response){
 var result=executionResult(response);
 if(!result||typeof result!=="object"){return null;}
 if(typeof result.text==="string"){return result.text.trim();}
 if(result.path&&Object.prototype.hasOwnProperty.call(result,"exists")){
  var meta="I inspected "+result.path+"."+NL+NL+"Exists: "+(result.exists?"yes":"no")+NL+"Type: "+(result.is_dir?"folder":result.is_file?"file":"unknown");
  if(result.size!==undefined){meta+=NL+"Size: "+result.size+" bytes";}
  return meta;
 }
 if(Array.isArray(result.entries)){
  var lines=[],i;
  for(i=0;i<result.entries.length;i+=1){
   var entry=result.entries[i];
   if(typeof entry==="string"){lines.push(entry);}
   else if(entry&&entry.name){lines.push(entry.name);}
   else if(entry&&entry.path){lines.push(entry.path);}
   else{lines.push(JSON.stringify(entry));}
  }
  return "Here is what I found:"+NL+NL+(lines.length?lines.map(function(x){return "• "+x;}).join(NL):"The folder is empty.");
 }
 return null;
}
function showExecution(response){
 var payload={ok:response&&response.ok,paused:response&&response.paused,permission_required:response&&response.permission_required,checkpoint_id:response&&response.checkpoint_id,pipeline:response&&response.pipeline,execution:response&&response.execution,verification:response&&response.verification,error:response&&response.error};
 $("execution").innerHTML="<pre>"+esc(JSON.stringify(payload,null,2))+"</pre>";
}
function system(){
 return api("/v1/console/core").then(function(data){
  $("status").innerHTML='<span class="status-dot"></span> Core + Body online';
  var core=data.core||{},body=data.body||{};
  $("system").innerHTML='<b>Core '+esc(core.version||"10.0.0")+"</b><br>"+esc(core.brain||"Hashtag")+"<br><br><b>Executor</b><br>"+esc(body.name||"Hashtag the Executor")+"<br>"+esc(body.version||"1.3.0")+'<br><span style="color:#8fa0bb">'+esc(data.pending_permissions||0)+" pending permissions</span>";
 }).catch(function(error){
  $("status").innerHTML='<span class="status-error">●</span> Core offline';
  $("system").textContent=error.message||"Unable to reach Core";
 });
}
function permissions(){
 return api("/v1/body/permissions/pending").then(function(data){
  var pending=Array.isArray(data.pending)?data.pending:[];
  var next={};
  pending.forEach(function(p){next[p.request_id]=true;});
  lastPendingIds=next;
  if(!pending.length){
   $("permissions").innerHTML='<div class="card">No pending requests.</div>';
   return;
  }
  var html="",i;
  for(i=0;i<pending.length;i+=1){
   var p=pending[i];
   html+='<div class="card permission-card"><div class="permission-title"><span class="permission-icon">!</span><span>Permission required</span></div><div class="permission-meta"><b>'+esc(p.operation)+'</b><br>'+esc(p.purpose||"Hashtag requested access to complete this operation.")+'</div><div class="permission-resource">'+esc(p.resource)+'</div><div class="permission-actions"><button class="allow" data-permission-action="decide" data-request-id="'+esc(p.request_id)+'" data-allowed="true" data-scope="once">Allow once</button><button class="task" data-permission-action="decide" data-request-id="'+esc(p.request_id)+'" data-allowed="true" data-scope="task">Allow for task</button><button class="deny" data-permission-action="decide" data-request-id="'+esc(p.request_id)+'" data-allowed="false" data-scope="once">Deny</button></div><div class="permission-note">Hashtag will continue only after your approval.</div></div>';
  }
  $("permissions").innerHTML=html;
 }).catch(function(error){$("permissions").textContent=error.message||"Unable to load permissions";});
}
function isPermissionPaused(response){
 if(!response||typeof response!=="object"){return false;}
 if(response.permission_required===true||response.paused===true){return true;}
 if(response.status==="permission_required"){return true;}
 var keys=["pipeline","execution","result","plan","graph"];
 for(var i=0;i<keys.length;i+=1){
  var value=response[keys[i]];
  if(value&&typeof value==="object"&&isPermissionPaused(value)){return true;}
 }
 return false;
}
function operationName(response){
 if(!response||typeof response!=="object"){return "";}
 if(response.operation){return String(response.operation);}
 if(response.execution&&response.execution.audit&&response.execution.audit.operation){return String(response.execution.audit.operation);}
 if(response.result&&response.result.execution&&response.result.execution.audit&&response.result.execution.audit.operation){return String(response.result.execution.audit.operation);}
 return "";
}
function decide(requestId,allowed,scope){
 if(allowed){setFlowApproved();}
 else{setFlowError("Permission denied. Task stopped.");}
 var buttons=document.querySelectorAll("[data-request-id='"+CSS.escape(requestId)+"']");
 buttons.forEach(function(b){b.disabled=true;});
 return api("/v1/console/permission/decide",{method:"POST",body:JSON.stringify({request_id:requestId,allowed:allowed,scope:scope})}).then(function(response){
  var r=(response&&response.result&&typeof response.result==="object")?response.result:response;
  showExecution(r);
  if(allowed){
   var details=resultText(r);
   if(r&&r.ok){
    setFlowDone();
    if(details){addMessage("assistant",details,"result");}
    else{addMessage("assistant","Done. Hashtag completed the request.");}
   }else if(isPermissionPaused(r)){
    addFlowMessage();
   }else{
    setFlowError(r&&r.message?r.message:"The operation could not be completed.");
   }
  }
  return Promise.all([permissions(),system()]);
 }).catch(function(error){
  setFlowError("Permission action failed: "+(error.message||error));
  return permissions();
 });
}
var activeTargetRepo = localStorage.getItem("hashtag_target_repo") || "hashtag-movies/Hashtag-core";
var cachedRepos = [];

function send(){
 var input=$("input"),message=input.value.trim();
 if(!message){return;}
 input.value="";
 var sendTime=new Date();
 var startTime=Date.now();
 addMessage("user",message,null,{sentAt:formatClock(sendTime)});
 $("send").disabled=true;
 $("send").classList.add("busy");
 $("send").querySelector(".send-icon").textContent="⟳";
 var thinking=addMessage("assistant","Hashtag is thinking...","thinking");
 var ctx = {
  target_repo: activeTargetRepo,
  repository: activeTargetRepo
 };
 api("/v1/console/request",{method:"POST",body:JSON.stringify({request:message,body_id:"hashtag-executor",context:ctx})}).then(function(response){
  var durationMs=Date.now()-startTime;
  var durationStr=(durationMs/1000).toFixed(1)+"s";
  var compTime=formatClock();
  var metaObj={duration:durationStr,completedAt:compTime};
  if(thinking&&thinking.parentNode){thinking.parentNode.removeChild(thinking);}
  showExecution(response);
  if(isPermissionPaused(response)){
   addFlowMessage();
   return permissions();
  }
  var details=resultText(response);
  if(details){addMessage("assistant",details,"result",metaObj);}
  else if(response&&response.ok){addMessage("assistant","Done. Hashtag completed the request.",null,metaObj);}
  else{addMessage("assistant",response&&response.message?response.message:"Hashtag returned a result.",null,metaObj);}
  return permissions();
 }).catch(function(error){
  var durationMs=Date.now()-startTime;
  var durationStr=(durationMs/1000).toFixed(1)+"s";
  if(thinking&&thinking.parentNode){thinking.parentNode.removeChild(thinking);}
  addMessage("assistant","I could not reach Hashtag Core: "+(error.message||error),null,{duration:durationStr,completedAt:formatClock()});
  return Promise.resolve();
 }).then(function(){
  $("send").disabled=false;
  $("send").classList.remove("busy");
  $("send").querySelector(".send-icon").textContent="➜";
  input.focus();
 });
}
function loadRepositories(selectEl, currentSelected){
 if(!selectEl){return;}
 api("/v1/github/repositories").then(function(res){
  if(res&&res.ok&&res.repositories&&res.repositories.length){
   cachedRepos=res.repositories;
   var opts="";
   cachedRepos.forEach(function(r){
    var sel=(r.full_name===currentSelected)?" selected":"";
    opts+='<option value="'+esc(r.full_name)+'"'+sel+'>'+esc(r.full_name)+'</option>';
   });
   selectEl.innerHTML=opts;
  }
 }).catch(function(){});
}
function githubStatus(){
 api("/v1/github/status").then(function(data){
  var el=$("github");
  if(!el){return;}
  if(data.connected){
   if(data.target_repo){activeTargetRepo=data.target_repo;}
   var currentSelect=$("target-repo-select");
   if(currentSelect){
    // Dropdown is already present, just ensure repositories are loaded
    if(!cachedRepos.length){loadRepositories(currentSelect,activeTargetRepo);}
    return;
   }
   el.innerHTML='<div style="color:var(--good);font-weight:700">✓ Connected</div>'
    +'<div style="margin-top:4px;color:var(--muted)">User: <b style="color:var(--text)">@'+esc(data.username)+'</b></div>'
    +'<div style="margin-top:8px">'
    +'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
    +'<span style="font-size:11px;color:var(--muted);font-weight:600">Target Repository:</span>'
    +'</div>'
    +'<div style="position:relative">'
    +'<select id="target-repo-select" style="width:100%;appearance:none;-webkit-appearance:none;background:rgba(18,28,48,0.95);border:1px solid rgba(120,169,255,0.3);color:#edf4ff;padding:7px 26px 7px 9px;border-radius:9px;font-size:11px;font-weight:600;cursor:pointer;outline:none;box-shadow:0 4px 14px rgba(0,0,0,0.25)">'
    +'<option value="'+esc(activeTargetRepo)+'">'+esc(activeTargetRepo)+'</option>'
    +'</select>'
    +'<span style="position:absolute;right:9px;top:50%;transform:translateY(-50%);pointer-events:none;color:var(--accent);font-size:11px">▾</span>'
    +'</div>'
    +'</div>';

   var sel=$("target-repo-select");
   if(sel){
    loadRepositories(sel,activeTargetRepo);
    sel.onchange=function(){
     var val=sel.value;
     activeTargetRepo=val;
     localStorage.setItem("hashtag_target_repo",val);
     api("/v1/github/target_repo",{method:"POST",body:JSON.stringify({target_repo:val})}).catch(function(){});
    };
   }
  } else {
   el.innerHTML='<div style="color:var(--danger);font-weight:700">✕ Not Connected</div>'
    +'<div style="font-size:11px;color:#8fa0bb;margin:6px 0">Connect with GitHub Personal Access Token (PAT) or link your PC:</div>'
    +'<input id="gh-token" type="password" placeholder="ghp_... (GitHub Token)" style="width:100%;margin-bottom:6px;background:rgba(0,0,0,0.3);border:1px solid rgba(120,169,255,0.2);color:#fff;padding:6px;border-radius:6px;font-size:11px">'
    +'<button id="gh-token-btn" style="width:100%;background:var(--accent);color:#000;border:0;border-radius:6px;padding:6px;font-weight:700;cursor:pointer;font-size:11px">Connect Token</button>';
   var btn=$("gh-token-btn");
   if(btn){
    btn.onclick=function(){
     var t=$("gh-token").value.trim();
     if(!t){alert("Enter your GitHub Personal Access Token (starts with ghp_ or github_pat_)");return;}
     btn.disabled=true;btn.textContent="Connecting...";
     api("/v1/github/login",{method:"POST",body:JSON.stringify({token:t})}).then(function(res){
      alert(res.message);
      githubStatus();
     }).catch(function(err){
      alert("Error: "+(err.message||err));
      btn.disabled=false;btn.textContent="Connect Token";
     });
    };
   }
  }
 }).catch(function(){});
}
function copyPsCommand(){
 var text="irm " + window.location.origin + "/connect.ps1 | iex";
 if(navigator.clipboard && navigator.clipboard.writeText){
  navigator.clipboard.writeText(text).then(function(){
   alert("Copied PowerShell command! Paste into PowerShell and press Enter to link your PC.");
  }).catch(function(){
   prompt("Copy this PowerShell command:", text);
  });
 } else {
  prompt("Copy this PowerShell command:", text);
 }
}
function pcConnectorStatus(){
 var el=$("pc_drive");
 if(!el){return;}
 api("/v1/connector/status").then(function(res){
  if(res&&res.connected){
   var info=res.info||{};
   var drives=(info.drives||["C:\\\\"]).join(", ");
   el.innerHTML='<div style="color:var(--good);font-weight:700">🟢 PC Linked</div>'
    +'<div style="font-size:11px;color:#a5b6cf;margin-top:4px"><b>Host:</b> '+esc(info.hostname||"Local PC")+' ('+esc(info.system||"Windows")+')</div>'
    +'<div style="font-size:11px;color:#a5b6cf"><b>Drives:</b> '+esc(drives)+'</div>'
    +'<div style="font-size:10px;color:var(--muted);margin-top:4px">User: '+esc(info.username||"User")+'</div>';
  } else {
   var psCmd="irm "+location.origin+"/connect.ps1 | iex";
   el.innerHTML='<div style="color:#f2c76d;font-weight:700">⚪ PC Not Linked</div>'
    +'<div style="font-size:11px;color:#8fa0bb;margin:6px 0">Run in PowerShell on your PC to link local drives:</div>'
    +'<div id="ps-cmd-box" style="background:#091220;border:1px solid rgba(120,169,255,0.3);border-radius:6px;padding:6px 8px;font-family:monospace;font-size:10px;color:#80d4ff;word-break:break-all;user-select:all;cursor:pointer" title="Click to copy">'
    +esc(psCmd)+'</div>'
    +'<button id="copy-ps-btn" style="margin-top:6px;width:100%;background:linear-gradient(135deg,#78a9ff,#5285e8);color:#06101e;padding:7px;border-radius:8px;font-size:11px;font-weight:800;border:0;cursor:pointer">📋 Copy PowerShell Command</button>'
    +'<div style="margin-top:6px;font-size:10px;color:#ff9e9e">⚠️ Windows 11 Smart App Control blocks .bat downloads. Running via PowerShell directly bypasses the block safely.</div>';

   var psBox=$("ps-cmd-box");
   var copyBtn=$("copy-ps-btn");
   if(copyBtn){ copyBtn.onclick=copyPsCommand; }
   if(psBox){ psBox.onclick=copyPsCommand; }
  }
 }).catch(function(){});
}
function initialize(){
 $("send").onclick=send;
 $("permissions").addEventListener("click",function(event){
  var target=event.target;
  if(!target||!target.getAttribute||target.getAttribute("data-permission-action")!=="decide"){return;}
  event.preventDefault();
  decide(target.getAttribute("data-request-id"),target.getAttribute("data-allowed")==="true",target.getAttribute("data-scope")||"once");
 });
 $("input").addEventListener("keydown",function(event){
  if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();send();}
 });
 system();
 permissions();
 githubStatus();
 pcConnectorStatus();
 api("/v1/console/register",{method:"POST"}).catch(function(){});
 window.setInterval(permissions,1200);
 window.setInterval(system,5000);
 window.setInterval(githubStatus,8000);
 window.setInterval(pcConnectorStatus,3500);
}
if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",initialize);}else{initialize();}
})();

</script></body></html>
"""
