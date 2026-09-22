(() => {
  'use strict';
  const root=document.querySelector('[data-book]');if(!root)return;
  const $=id=>document.getElementById(id),nodes=[...document.querySelectorAll('[data-paragraph]')];
  const originals=nodes.map(p=>[...p.childNodes].map(n=>({node:n,text:n.textContent})));
  const storageKey='scriptlibrary:'+root.dataset.book;
  let lastPractice='greek';
  const profileSelect=$('profile');
  for(const [id,p] of Object.entries(Scriptbridge.profiles)){const option=document.createElement('option');option.value=id;option.textContent=p.label;profileSelect.append(option);}
  profileSelect.value='greek';
  try{const saved=JSON.parse(localStorage.getItem(storageKey)||'null');if(saved){$('profile').value=saved.profile==='original'?'original':Scriptbridge.settings(saved).profile;if(saved.mode==='progressive')$('mode').value='progressive';$('density').value=Scriptbridge.settings(saved).percent;}}catch{}
  function update(){
    const profile=$('profile').value,percent=Number($('density').value),source=root.dataset.language;
    if(profile!=='original')lastPractice=profile;
    let total=0,replaced=0,letters=0;
    originals.forEach((runs,index)=>{
      // One seed per paragraph; each inline run is handled identically by the PDF renderer.
      runs.forEach((run,j)=>{
        const opt={source,profile,percent:profile==='original'?0:$('mode').value==='progressive'?ScriptlibraryEditions.percent('progressive',index,nodes.length):percent,seed:`${root.dataset.book}:${nodes[index].dataset.paragraph}:${j}`};
        const out=Scriptbridge.transform(run.text,opt);total+=out.eligible;replaced+=out.replaced;letters+=out.letters;
        run.node.textContent=out.text;
      });
    });
    $('density-value').value=$('mode').value==='progressive'?'20–100%':percent+'%';$('density').disabled=profile==='original'||$('mode').value==='progressive';
    $('original').textContent=profile==='original'?'Resume practice':'Show original';
    $('reading-status').textContent=profile==='original'?'Original text. No letters have been changed.':`${replaced.toLocaleString()} of ${total.toLocaleString()} eligible letters changed (${letters?(100*replaced/letters).toFixed(1):0}% of all letters).`;
    const p=Scriptbridge.profiles[profile];
    $('mapping-note').textContent=p?p.note:'The unchanged original text.';
    $('letter-key').textContent=p?Object.entries(p.map).map(([a,b])=>`${a} → ${b}`).join('   ·   '):'';
    try{localStorage.setItem(storageKey,JSON.stringify({profile,percent,mode:$('mode').value}));}catch{}
  }
  $('profile').addEventListener('change',update);$('mode').addEventListener('change',update);$('density').addEventListener('input',update);
  $('original').addEventListener('click',()=>{$('profile').value=$('profile').value==='original'?lastPractice:'original';update();});
  update();
})();
