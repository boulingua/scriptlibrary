(() => {
  'use strict';
  const root=document.querySelector('[data-book]');if(!root)return;
  const $=id=>document.getElementById(id),nodes=[...document.querySelectorAll('[data-paragraph]')];
  const originals=nodes.map(p=>[...p.childNodes].map(n=>({node:n,text:n.textContent})));
  const storageKey='scriptlibrary:'+root.dataset.book;
  let lastPractice='greek';
  try{const saved=JSON.parse(localStorage.getItem(storageKey)||'null');if(saved){if(saved.profile==='original'||Object.hasOwn(Scriptbridge.profiles,saved.profile))$('profile').value=saved.profile;$('density').value=Scriptbridge.settings(saved).percent;}}catch{}
  function update(){
    const profile=$('profile').value,percent=Number($('density').value),source=root.dataset.language;
    if(profile!=='original')lastPractice=profile;
    let total=0,replaced=0,letters=0;
    originals.forEach((runs,index)=>{
      // One seed per paragraph; each inline run is handled identically by the PDF renderer.
      runs.forEach((run,j)=>{
        const opt={source,profile,percent:profile==='original'?0:percent,seed:`${root.dataset.book}:${nodes[index].dataset.paragraph}:${j}`};
        const out=Scriptbridge.transform(run.text,opt);total+=out.eligible;replaced+=out.replaced;letters+=out.letters;
        run.node.textContent=out.text;
      });
    });
    $('density-value').value=percent+'%';$('density').disabled=profile==='original';
    $('original').textContent=profile==='original'?'Resume practice':'Show original';
    $('reading-status').textContent=profile==='original'?'Original text. No letters have been changed.':`${replaced.toLocaleString()} of ${total.toLocaleString()} eligible letters changed (${letters?(100*replaced/letters).toFixed(1):0}% of all letters).`;
    const p=Scriptbridge.profiles[profile];
    $('mapping-note').textContent=p?p.note:'The unchanged original text.';
    $('letter-key').textContent=p?Object.entries(p.map).map(([a,b])=>`${a} → ${b}`).join('   ·   '):'';
    try{localStorage.setItem(storageKey,JSON.stringify({profile,percent}));}catch{}
  }
  $('profile').addEventListener('change',update);$('density').addEventListener('input',update);
  $('original').addEventListener('click',()=>{$('profile').value=$('profile').value==='original'?lastPractice:'original';update();});
  update();
})();
