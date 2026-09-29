function createOCRHashtagBody(options){
  options=options||{};
  const getInput=options.getText||(()=>document.querySelector("#inputText")?.value||"");
  const setOutput=options.setOutput||(text=>{const el=document.querySelector("#outputText");if(el)el.value=text});
  let workingText=getInput();
  const transform=fn=>{const lines=workingText.split(/\r?\n/);const out=fn(lines);workingText=out.join("\n");return{text:workingText,lineCount:out.length}};
  const manifest={id:"ocr-record-formatter",name:"OCR Record Formatter",version:"32",description:"Messy OCR text formatting and large TXT processing body.",capabilities:[
    {id:"text.remove_digits",description:"Remove every digit 0-9 from every line."},{id:"text.remove_letters",description:"Remove alphabetic characters."},{id:"text.replace",description:"Replace literal text with another literal text."},{id:"text.regex_replace",description:"Apply a user-requested safe regex replacement."},{id:"text.conditional_prepend",description:"Prepend text to lines containing a requested value."},{id:"filter.keep_contains",description:"Keep only lines containing requested values."},{id:"filter.remove_contains",description:"Remove lines containing requested values."},{id:"format.remove_duplicates",description:"Remove duplicate lines."},{id:"format.remove_number_only",description:"Remove lines containing only numbers."},{id:"format.remove_empty_lines",description:"Remove empty lines."},{id:"format.keep_before",description:"Keep text before a separator."},{id:"format.keep_after",description:"Keep text after a separator."},{id:"format.extract_between",description:"Extract text between two markers."},{id:"format.lowercase",description:"Convert output to lowercase."},{id:"format.uppercase",description:"Convert output to uppercase."},{id:"format.normalize_spaces",description:"Normalize repeated whitespace."},{id:"format.trim",description:"Trim surrounding whitespace from each line."},{id:"format.pick_fields",description:"Select fields by position and join them."},{id:"format.join_blocks",description:"Join each N lines with a delimiter."},{id:"format.sort_lines",description:"Sort lines alphabetically."}
  ]};
  const contains=(values,line,cs)=>(values||[]).some(v=>cs?line.includes(String(v)):line.toLowerCase().includes(String(v).toLowerCase()));
  const handlers={
    "text.remove_digits":()=>transform(ls=>ls.map(x=>x.replace(/[0-9]/g,""))),
    "text.remove_letters":()=>transform(ls=>ls.map(x=>x.replace(/[A-Za-z]/g,""))),
    "text.replace":({old,new:rep})=>transform(ls=>ls.map(x=>x.split(String(old??"")).join(String(rep??"")))),
    "text.regex_replace":({pattern,to,flags})=>transform(ls=>{let r;try{r=new RegExp(String(pattern),String(flags||"g"))}catch(e){return ls}return ls.map(x=>x.replace(r,String(to??"")))}),
    "text.conditional_prepend":({contains:v,prefix})=>transform(ls=>ls.map(x=>x.toLowerCase().includes(String(v).toLowerCase())?String(prefix||"")+x:x)),
    "filter.keep_contains":({values,caseSensitive})=>transform(ls=>ls.filter(x=>contains(values,x,!!caseSensitive))),
    "filter.remove_contains":({values,caseSensitive})=>transform(ls=>ls.filter(x=>!contains(values,x,!!caseSensitive))),
    "format.remove_duplicates":()=>transform(ls=>Array.from(new Set(ls))),
    "format.remove_number_only":()=>transform(ls=>ls.filter(x=>!/^[ \t]*\d+(?:\.\d+)?[ \t]*$/.test(x))),
    "format.remove_empty_lines":()=>transform(ls=>ls.filter(x=>x.trim())),
    "format.keep_before":({separator})=>transform(ls=>ls.map(x=>{const i=x.indexOf(String(separator));return i>=0?x.slice(0,i).trimEnd():x})),
    "format.keep_after":({separator})=>transform(ls=>ls.map(x=>{const i=x.indexOf(String(separator));return i>=0?x.slice(i+String(separator).length).trimStart():x})),
    "format.extract_between":({start,end})=>transform(ls=>ls.map(x=>{const a=x.indexOf(String(start));if(a<0)return x;const b=x.indexOf(String(end),a+String(start).length);return b<0?x:x.slice(a+String(start).length,b)})),
    "format.lowercase":()=>transform(ls=>ls.map(x=>x.toLowerCase())),"format.uppercase":()=>transform(ls=>ls.map(x=>x.toUpperCase())),"format.normalize_spaces":()=>transform(ls=>ls.map(x=>x.replace(/\s+/g," ").trim())),"format.trim":()=>transform(ls=>ls.map(x=>x.trim())),
    "format.pick_fields":({fields,delimiter})=>transform(ls=>ls.map(line=>{const p=line.includes(":")?line.split(":"):line.includes("|")?line.split("|"):line.trim().split(/\s+/);return(fields||[]).map(n=>p[n-1]||"").join(delimiter||":")})),
    "format.join_blocks":({size,delimiter})=>transform(ls=>{const n=Math.max(1,Number(size)||1),d=String(delimiter??":");const out=[];for(let i=0;i<ls.length;i+=n){const g=ls.slice(i,i+n);g.length===n?out.push(g.join(d)):out.push(...g)}return out}),
    "format.sort_lines":({order})=>transform(ls=>{const a=ls.slice().sort((x,y)=>x.localeCompare(y,undefined,{numeric:true,sensitivity:"base"}));return order==="desc"?a.reverse():a})
  };
  return{manifest,handlers,inspect:()=>({text:workingText,lineCount:workingText.split(/\r?\n/).length}),reset:()=>{workingText=getInput()},finalize:()=>{setOutput(workingText);return{text:workingText,lineCount:workingText.split(/\r?\n/).length}}};
}
