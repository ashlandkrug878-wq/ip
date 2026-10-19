(() => {
  'use strict';
  const data=JSON.parse(document.getElementById('research-payload').textContent);
  const $=id=>document.getElementById(id);
  let selected=3;
  const renderTest=()=>{
    const t=data.tests[selected];
    $('test-image').src=t.generated_image_path;
    $('test-image').alt=(t.input_mode==='text_only'?'纯文字':'参考辅助')+' v'+t.version+' 实际生成，未通过';
    $('test-zoom').dataset.image=t.generated_image_path;
    $('test-zoom').dataset.caption=$('test-image').alt+'。'+t.observation;
    $('test-mode').textContent=(t.input_mode==='text_only'?'纯文字':'参考辅助')+' v'+t.version+' · 实际生成';
    $('test-dependency').textContent=t.input_mode==='text_only'?'无参考图输入 · 中文实测':'输入官方参考图 · 不证明纯文字通过';
    $('test-observation').textContent=t.observation;
    $('test-next').textContent=t.next_change;
    $('prompt-text').textContent=t.exact_prompt;
    $('copy-status').textContent='';
  };
  $('test-select').addEventListener('change',e=>{selected=Number(e.target.value);renderTest();});
  renderTest();
  $('copy-prompt').addEventListener('click',async()=>{
    try {await navigator.clipboard.writeText(data.tests[selected].exact_prompt);$('copy-status').textContent='已复制：未通过的测试词';}
    catch {const range=document.createRange();range.selectNodeContents($('prompt-text'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);$('copy-status').textContent='已选中文本，请使用系统复制';}
  });
  document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
    document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
    document.querySelectorAll('[data-product-group]').forEach(row=>{row.hidden=button.dataset.filter!=='all'&&row.dataset.productGroup!==button.dataset.filter;});
  }));
  const periods={year:{old:'2024',now:'2025',v1:'11.64885',v2:'29.29006',ratio:39.7706587,growth:'+151.44%',title:'2024 与 2025 全年',note:'2025 全年同比 · 原值计算',source:'年报印刷p27 / PDF第28页；原单位人民币千元。',ref:'s-annual2025',table:'sources/annual2025-p27.png'},half:{old:'2025 H1',now:'2026 H1',v1:'12.1817',v2:'16.3257',ratio:74.616564,growth:'+34.02%',title:'2025 与 2026 上半年',note:'2026 上半年同比 · 未经审计 · 原值计算',source:'中期公告印刷p30 / PDF第30页；原单位人民币千元。',ref:'s-h12026',table:'sources/interim2026-p30.png'}};
  document.querySelectorAll('[data-period]').forEach(button=>button.addEventListener('click',()=>{
    document.querySelectorAll('[data-period]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
    const p=periods[button.dataset.period];
    $('chart-title').textContent=p.title;$('bar-old-label').textContent=p.old;$('bar-new-label').textContent=p.now;
    $('bar-old-value').textContent=p.v1;$('bar-new-value').textContent=p.v2;$('bar-old').style.width=p.ratio+'%';
    $('growth-value').textContent=p.growth;$('growth-note').textContent=p.note;
    const source=$('chart-source');source.replaceChildren(document.createTextNode(p.source+' '));
    const a=document.createElement('a');a.href='#'+p.ref;a.textContent='[原件]';source.append(a,document.createTextNode(' '));
    const img=document.createElement('a');img.href=p.table;img.target='_blank';img.rel='noopener';img.textContent='查看收入表 ↗';source.append(img);
  }));
  const dialog=$('lightbox');
  document.addEventListener('click',e=>{
    const button=e.target.closest('[data-image]');
    if(button){$('lightbox-image').src=button.dataset.image;$('lightbox-image').alt=button.dataset.caption;$('lightbox-caption').textContent=button.dataset.caption;dialog.showModal();}
    const link=e.target.closest('a[href^="#"]');
    if(link){const id=link.getAttribute('href').slice(1);const target=$(id);if(target){let parent=target.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}}}
  });
  $('close-lightbox').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target===dialog){const box=dialog.getBoundingClientRect();if(e.clientX<box.left||e.clientX>box.right||e.clientY<box.top||e.clientY>box.bottom)dialog.close();}});
  function openHash(){const target=$(decodeURIComponent(location.hash.slice(1)));if(!target)return;let parent=target.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));}
  if(location.hash)openHash();
  window.addEventListener('hashchange',openHash);
  if('IntersectionObserver' in window){const links=[...document.querySelectorAll('.section-nav a')];const observer=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){links.forEach(a=>a.classList.toggle('current',a.hash==='#'+entry.target.id));}}},{rootMargin:'-80px 0px -60% 0px',threshold:0});links.forEach(a=>{const section=$(a.hash.slice(1));if(section)observer.observe(section);});}
})();
