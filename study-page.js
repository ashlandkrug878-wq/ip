const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const safeUrl=u=>/^https?:\/\//i.test(String(u||""))?u:null;
const jn=v=>Array.isArray(v)?v.join("、"):(v??"");
const TIER={quick:"速查",standard:"标准",deep:"深挖"};
function renderStudyPage(c){
  const sec=(t,h)=>h?`<div class="sec"><h3>${t}</h3>${h}</div>`:"";
  const kv=pairs=>`<div class="kv">${pairs.filter(([,v])=>v!=null&&v!=="").map(([k,v])=>`<span>${k}</span><span>${esc(v)}</span>`).join("")}</div>`;
  const S={};(c.sources||[]).forEach(x=>S[x.id]=x);
  const refs=ids=>(ids||[]).map(i=>S[i]&&safeUrl(S[i].url)?`<a href="${esc(S[i].url)}" target="_blank" rel="noopener noreferrer">${esc(S[i].publisher||"来源")} ↗</a>`:"").join(" ");
  const TY={fact:"已核实",self_report:"官方或作者自述",inference:"研究推断",hypothesis:"待验证"};
  const f=c.form||{},t=c.theory||{},fs=c.for_skills||{};
  $("studyContent").innerHTML=`<div class="dhead">
     <div class="row-between"><h1 id="dTitle">${esc(c.name)} <span class="tierchip">${esc(TIER[c.tier]||c.tier)}${c.status==="partial"?" · 未完成":""}</span></h1></div>
     <div class="note">${esc(jn(c.aliases))} · 截止 ${esc(c.cutoff_date)}</div>
     <div class="expr">${esc(c.summary)}</div>
   </div>
   <div class="dbody">
    ${sec("给我们三个 skill 的启发",kv([["表达 lab",fs.lab],["找形 form",fs.form],["定型 studio",fs.studio],["别撞的组合",c.collide_combo]]))}
    ${sec("权属与起源",kv([["作者",c.owner?.creator],["运营",c.owner?.operator],["关系",c.owner?.relation],["起盘路径",jn(c.origin?.path)],["起源",(c.origin?.year||"")+" · "+(c.origin?.story||"")]]))}
    ${(c.timeline||[]).length?sec("时间线",`<div class="layers">${c.timeline.map(e=>`<div><span>${esc(e.date)}</span><span>${esc(e.event)} <span class="note">${esc(TY[e.type]||"")}</span> ${refs(e.sources)}</span></div>`).join("")}</div>`):""}
    ${sec("表达与内核",kv([["表达",c.expression?.line],["句式",c.expression?.sentence_type],["性格",c.core?.personality],["情绪",c.core?.emotion],["它在做什么",c.core?.action],["钟摆",(c.pendulum?.position||"")+" · "+(c.pendulum?.against||"")]]))}
    ${sec("洞察与圈层",kv([["状态",c.insight?.state],["矛盾",c.insight?.conflict],["没说出口的话",c.insight?.unsaid],["是谁",c.circle?.who],["已经在买",c.circle?.buy],["怎么晒",c.circle?.share],["破圈",c.circle?.breakout]]))}
    ${sec("外形（五条轴）",kv([["原型",f.archetype],["轮廓",f.silhouette],["记忆点",jn(f.mark_position)+" · "+(f.mark||"")],["五官",f.face],["情绪",f.emotion],["反常点",f.odd],["细节密度",f.density],["命名",f.naming],["单角色或群",f.group]]))}
    ${sec("色彩、材质、产品",kv([["配色方式",c.color?.mode],["主色",c.color?.main],["签名色",c.color?.signature],["说明",c.color?.notes],["材质",c.materials],["主载体",c.carrier?.primary],["次载体",c.carrier?.secondary],["首发品类",c.product?.first_category],["爆款品类",c.product?.hit_category],["爆款",c.product?.hit_product],["价格",c.product?.price_band]]))}
    ${(c.numbers||[]).length?sec("数字",`<div class="layers">${c.numbers.map(n=>`<div><span>${esc(n.period)}</span><span>${esc(n.metric)}：${esc(n.value)} ${esc(n.unit)} <span class="note">${esc(TY[n.type]||"")}</span> ${refs(n.sources)}</span></div>`).join("")}</div>`):""}
    ${(c.mechanisms||[]).length?sec("机制",`<div class="layers">${c.mechanisms.map(m=>`<div><span>${esc(TY[m.type]||m.type)}</span><span>${esc(m.claim)}<br><span class="note">依据：${esc(m.evidence)}；边界：${esc(m.boundary)}</span> ${refs(m.sources)}</span></div>`).join("")}</div>`):""}
    ${sec("用你的理论看",kv([["外壳",t.shell],["内核",t.core],["有没有别人的影子",t.shadow],["表层给路人",t.two_layers?.surface],["深层给圈层",t.two_layers?.deep],["相信腿不相信嘴",t.validation]]))}
    ${sec("反例",esc(c.counterexamples))}
    ${(c.gaps||[]).length?sec("还没查清的",`<ul>${c.gaps.map(g=>`<li>${esc(g)}</li>`).join("")}</ul>`):""}
    ${sec("来源",`<div class="links">${(c.sources||[]).filter(x=>safeUrl(x.url)).map(x=>`<a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">${esc(x.title)} ↗</a>`).join("")}</div>`)}
   </div>`;
}
(async()=>{
 const id=new URLSearchParams(location.search).get("id");
 try{
  if(!id||!/^[-a-zA-Z0-9_]+$/.test(id))throw new Error("未找到这份研究");
  const r=await fetch("data/studies/"+encodeURIComponent(id)+".json",{cache:"no-cache"});
  if(!r.ok)throw new Error("研究暂时无法载入，请返回研究库重试");
  const c=await r.json();
  const url=studyReportUrl(c);
  if(url){location.replace(url);return;}
  document.title=(c.name||"IP研究")+" · 研究库";
  renderStudyPage(c);
 }catch(e){$("studyContent").textContent=e.message;}
})();
