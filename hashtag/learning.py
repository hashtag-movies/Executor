import re,time
class SkillLearner:
    TARGET_RE=re.compile(r'\b(?:remove|delete|erase|strip|eliminate|discard)\s+([A-Za-z0-9_./@-]+)',re.I)
    TAKE_OUT_RE=re.compile(r'\b(?:take|get rid of)\s+([A-Za-z0-9_./@-]+)\s+(?:out|of)\b',re.I)
    @staticmethod
    def signature(request):
        s=(request or '').lower();s=re.sub(r'[^a-z0-9\s]',' ',s)
        s=re.sub(r'\b(the|a|an|please|just|whole|entire|text|file|document|from|every|each|all|my|this|that|input|content)\b',' ',s)
        s=re.sub(r'\b(remove|delete|erase|strip|eliminate|discard)\s+([a-z0-9_]+)',r'\1 <target>',s)
        s=re.sub(r'\b(take|get rid of)\s+([a-z0-9_]+)\s+(?:out|of)',r'\1 <target> out',s)
        return re.sub(r'\s+',' ',s).strip()[:240]
    @classmethod
    def extract_target(cls,request):
        text=(request or '').strip();m=cls.TARGET_RE.search(text)
        if m:return m.group(1).strip('"\'“”')
        m=cls.TAKE_OUT_RE.search(text)
        if m:return m.group(1).strip('"\'“”')
        return None
    @staticmethod
    def _template_action(action,request):
        cap=action.get('capability');args=dict(action.get('arguments') or {});target=SkillLearner.extract_target(request)
        if cap=='text.replace' and target and str(args.get('old','')).strip().casefold()==target.casefold():args['old']='$TARGET'
        return {'capability':cap,'arguments':args,'reason':action.get('reason','')[:1000]}
    @classmethod
    def generalize(cls,request,plan):return [cls._template_action(a,request) for a in plan.get('actions',[])]
    def __init__(self,memory):self.memory=memory
    def learn_from_success(self,tool_id,request,plan,verification,capabilities=None):
        if not verification.get('ok') or not plan.get('actions') or not self.memory:return None
        intent=self.signature(request)
        if not intent:return None
        required=sorted({str(a.get('capability')) for a in plan.get('actions',[]) if a.get('capability')})
        if capabilities is not None:
            available={str(c.get('id')) for c in capabilities}
            if not set(required).issubset(available):return None
        rec={'kind':'learned_skill','scope':'shared','tool_id':tool_id,'intent':intent,'request_example':(request or '')[:240],
             'template_actions':self.generalize(request,plan),'required_capabilities':required,
             'confidence':float(verification.get('confidence',0.92)),'learned_at':time.time()}
        self.memory.learn(rec);return rec
    def reuse(self,tool_id,request,capabilities=None):
        if not self.memory:return []
        intent=self.signature(request);target=self.extract_target(request)
        if not intent or not target:return []
        available={str(c.get('id')) for c in (capabilities or [])}
        for recipe in self.memory.find_skills_any(tool_id,intent):
            required=set(recipe.get('required_capabilities') or [])
            if required and not required.issubset(available):continue
            out=[]
            for raw in recipe.get('template_actions',[]):
                a={'capability':raw.get('capability'),'arguments':dict(raw.get('arguments') or {}),'reason':raw.get('reason') or 'Reused a learned generalized skill.','source':'learned'}
                for k,v in list(a['arguments'].items()):
                    if v=='$TARGET':a['arguments'][k]=target
                out.append(a)
            if out:return out
        return []
