// Kyphara translator (no Google banner). Used by index.html, privacy.html and terms.html.
// 1) hand-reviewed texts (FIX) win; 2) ready-made pack tr/<lang>.json (made with tools/pretranslate.py);
// 3) anything still missing is translated in a few big batches, all at the same time.
// The page stays hidden (small spinner) until every text is ready, so it never shows two languages.
(function(){
  function norm(c){c=(c||'en').toLowerCase();if(c.indexOf('zh')===0)return /tw|hk|mo|hant/.test(c)?'zh-TW':'zh-CN';var b=c.split('-')[0];return {fil:'tl',he:'iw',nb:'no',nn:'no',jv:'jw'}[b]||b;}
  var saved=null;try{saved=localStorage.getItem('kyphara-lang')}catch(e){}
  var lang=saved||norm((navigator.languages&&navigator.languages[0])||navigator.language);
  var KEY='kyphara-tr2-'+lang,cache={};
  try{cache=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
  var packP=null;
  function pack(){if(!packP)packP=fetch('tr/'+lang+'.json').then(function(r){return r.ok?r.json():{}}).catch(function(){return {}}).then(function(j){for(var k in j)if(!cache[k])cache[k]=j[k];});return packP;}
  function clean(t){return t.replace(/\s+/g,' ').trim();}
  function fixb(k,v){return (k.indexOf('Kyphara')>=0&&v.indexOf('Kyphara')<0&&k.indexOf('7')<0)?v.replace(/[^\s:,.;()]*7/,'Kyphara'):v;}
  function cap(k,s){return (/^[A-Z]/.test(k)&&s)?s.charAt(0).toUpperCase()+s.slice(1):s;}
  function gt(list){
    return fetch('https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl='+lang+'&dt=t&q='+encodeURIComponent(list.join('\n').replace(/Kyphara/g,'XQ7')))
      .then(function(r){if(!r.ok)throw r.status;return r.json();})
      .then(function(j){var out=j[0].map(function(x){return x[0]}).join('').split('\n');if(out.length!==list.length)throw 'split';return out.map(function(s){return s.trim().replace(/XQ7|Xq7|xq7/g,'Kyphara')});});
  }
  function batch(list){ // one request per ~1500 characters; if a batch comes back badly split, translate its lines one by one
    var chunks=[],cur=[],len=0;
    list.forEach(function(k){if(len+k.length>1500&&cur.length){chunks.push(cur);cur=[];len=0;}cur.push(k);len+=k.length+1;});
    if(cur.length)chunks.push(cur);
    return Promise.all(chunks.map(function(c){
      return gt(c).then(function(o){c.forEach(function(k,i){if(o[i])cache[k]=cap(k,fixb(k,o[i]));});})
        .catch(function(){return Promise.all(c.map(function(k){return gt([k]).then(function(o){if(o[0])cache[k]=cap(k,fixb(k,o[0]));}).catch(function(){});}));});
    }));
  }
  function nodes(root){var out=[],w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:function(n){var p=n.parentElement;if(!p||/^(SCRIPT|STYLE|NOSCRIPT)$/.test(p.tagName)||p.closest('[translate=no],.notranslate')||!/\p{L}/u.test(n.nodeValue))return NodeFilter.FILTER_REJECT;return NodeFilter.FILTER_ACCEPT;}});while(w.nextNode())out.push(w.currentNode);return out;}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(cache))}catch(e){}}
  function show(){document.documentElement.classList.remove('trw');}
  function run(root,FIX){
    FIX=FIX||{};
    if(lang==='en'){show();return Promise.resolve();}
    var ns=nodes(root);
    ns.forEach(function(n){if(n.__orig===undefined)n.__orig=n.nodeValue;});
    function look(n){var o=n.__orig,k=o.trim(),c=clean(o);return FIX[k]||FIX[c]||cache[c];}
    function apply(){ns.forEach(function(n){var v=look(n);if(v){var o=n.__orig;n.nodeValue=o.match(/^\s*/)[0]+v+o.match(/\s*$/)[0];}});}
    return pack().then(function(){
      var need=[];ns.forEach(function(n){if(!look(n)){var c=clean(n.__orig);if(need.indexOf(c)<0)need.push(c);}});
      if(!need.length)return;
      var b=batch(need);b.then(function(){apply();save();}); // late answers still get applied
      return Promise.race([b,new Promise(function(r){setTimeout(r,8000)})]);
    }).then(function(){apply();show();save();});
  }
  window.KyTr={lang:lang,run:run,norm:norm};
})();
