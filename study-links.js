/* Full reports open directly; cards without one get a standalone reading page. */
function studyReportUrl(card){
  const candidates=[card.web_url,...(card.sources||[]).filter(source=>["delivery-webpage","research-web"].includes(source.id)).map(source=>source.url)];
  for(const value of candidates){
    if(typeof value!=="string"||!/^https?:\/\//i.test(value))continue;
    try{const url=new URL(value);if(["http:","https:"].includes(url.protocol)&&!url.username&&!url.password)return url.href;}catch(_){}
  }
  return null;
}
function studyPageUrl(card){return studyReportUrl(card)||"study.html?id="+encodeURIComponent(card.id);}
