(function(global){
  class HashtagConnector {
    constructor(options){
      options=options||{};
      this.api=(options.api||"http://127.0.0.1:8775").replace(/\/+$/,'');
      this.key=options.apiKey||"";
      this.manifest=options.manifest||{};
      this.handlers=new Map();
      this.body=options.body||null;
      this.connected=false;
      this.token=null;
      this.onEvent=options.onEvent||function(){};
    }
    capability(id,handler){this.handlers.set(id,handler);return this;}
    async connect(){
      const r=await this._post('/v1/register',{manifest:this.manifest});
      if(!r.ok)throw new Error(r.error||'Hashtag connection failed');
      this.connected=true;this.token=r.token||null;
      this.onEvent({type:'connected',tool:this.manifest.id,brain:'Hashtag'});return r;
    }
    async ask(request,context){
      if(!this.connected) await this.connect();
      if(this.body?.reset) this.body.reset();
      let inputText=context?.inputText||this.body?.inspect?.()?.text||'';
      this.onEvent({type:'thinking',request,inputPreview:inputText.slice(0,500)});
      const plan=await this._post('/v1/plan',{tool_id:this.manifest.id,request:String(request||''),context:Object.assign({},context||{},{inputText})});
      if(!plan.ok)return plan;
      const execution={ok:true,results:[],input:{lineCount:inputText.split(/\r?\n/).length}};
      for(const action of (plan.actions||[])){
        const handler=this.handlers.get(action.capability);
        if(!handler){execution.ok=false;execution.error='Capability not implemented by body: '+action.capability;break;}
        try{
          const value=await handler(action.arguments||{},{action,request,plan,body:this.body});
          execution.results.push({capability:action.capability,ok:true,value});
          if(value?.ok===false){execution.ok=false;execution.error=value.message||'Capability failed';break;}
        }catch(e){const msg=String(e?.message||e);execution.ok=false;execution.error=msg;execution.results.push({capability:action.capability,ok:false,error:msg});break;}
      }
      if(this.body?.finalize)execution.final=this.body.finalize();
      if(this.body?.inspect)execution.output=this.body.inspect();
      const verification=await this._post('/v1/verify',{plan,execution});
      this.onEvent({type:'complete',plan,execution,verification});
      return {ok:verification.ok,plan,execution,verification};
    }
    async heartbeat(){return this._post('/v1/heartbeat',{tool_id:this.manifest.id});}
    async _post(path,body){
      const headers={'Content-Type':'application/json'};if(this.key)headers['X-Hashtag-Key']=this.key;
      const res=await fetch(this.api+path,{method:'POST',headers,body:JSON.stringify(body)});
      const text=await res.text();let data;try{data=JSON.parse(text)}catch(_){data={ok:false,error:text}}if(!res.ok)data.ok=false;return data;
    }
  }
  global.HashtagConnector=HashtagConnector;
})(window);
