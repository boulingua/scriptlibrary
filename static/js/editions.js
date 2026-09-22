/* Shared online/PDF edition schedule. MIT. */
(function(root){
  'use strict';
  const modes={ '20':{label:'20%',description:'20% of eligible letters throughout'},'100':{label:'100%',description:'100% of eligible letters throughout'},progressive:{label:'20–100%',description:'Gradually increases from 20% in the first paragraph to 100% in the last paragraph'}};
  function percent(mode,index,count){
    if(!Object.hasOwn(modes,mode))throw new Error('Unknown edition mode');
    return mode==='progressive'?20+80*index/Math.max(1,count-1):Number(mode);
  }
  const api={modes,percent};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ScriptlibraryEditions=api;
})(globalThis);
