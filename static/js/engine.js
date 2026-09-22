/* Scriptbridge 0.2.0. Shared unchanged with the reading library under MIT. */
(function (root) {
  'use strict';
  const profiles = {
    greek: { label: 'Modern Greek', language: 'el', map: {m:'μ',n:'ν',p:'π',t:'τ',k:'κ',f:'φ',l:'λ',r:'ρ',s:'σ',v:'β',z:'ζ',a:'α',i:'ι',o:'ο',e:'ε'}, note: 'Modern sounds: β is /v/, not /b/. ρ is a tapped or trilled r. Final σ becomes ς.' },
    nordic: { label: 'Nordic letters', language: 'nb', map: {'ö':'ø','è':'ä','ê':'ä','a':'æ'}, note: 'Norwegian ø for German ö; Swedish ä for French è/ê; Norwegian æ only in a small English /æ/ word list. Nordic languages do not share one pronunciation system.' }
  };
  profiles.cyrillic={label:'Cyrillic',language:'und-Cyrl',map:{b:'б',d:'д',f:'ф',k:'к',l:'л',m:'м',n:'н',p:'п',r:'р',s:'с',t:'т',z:'з',a:'а',o:'о',j:'ж'},note:'A shared introductory subset, not the alphabet of one language. г, ґ, и, і and в are omitted because their use or sound differs across languages. Sound matches remain approximate.'};
  profiles.polish={label:'Polish letters',language:'pl',map:{j:'ż',y:'j',w:'ł',z:'c'},note:'French j → ż, German z → c, consonantal English y → j and selected English w → ł. These are contextual sound matches, not visual substitutions.',staged:false};
  profiles.czech={label:'Czech letters',language:'cs',map:{j:'ž',y:'j',z:'c'},note:'French j → ž, German z → c and consonantal English y → j. Czech č, š and ř are not approximated by unrelated single letters.',staged:false};
  profiles.nordic.map={...profiles.nordic.map};
  profiles.nordic.note='Selected Nordic letters, not one alphabet: Norwegian/Danish ø for German ö; Swedish ä for French è/ê; Norwegian/Danish æ for selected English /æ/ words. Icelandic æ is /ai/ and is taught in the introduction only, not mixed into the same replacement rule. Icelandic þ and ð are not single-letter English matches.';
  profiles.nordic.staged=false;
  const letters = /\p{L}/u;
  const vowel = /[aeiouyäöüàâéèêëîïôùûœæ]/u;
  const language = value => ({eng:'en',fra:'fr',fre:'fr',deu:'de',ger:'de'}[String(value).toLowerCase()] || String(value || '').toLowerCase().split(/[-_]/)[0]);
  function hash(s) {
    let h = 2166136261;
    for (const c of s) { h ^= c.codePointAt(0); h = Math.imul(h, 16777619); }
    h ^= h >>> 16; h = Math.imul(h, 0x7feb352d); h ^= h >>> 15;
    return h >>> 0;
  }
  function settings(input = {}) {
    return {profile: input.profile==='icelandic' ? 'nordic' : ['russian','ukrainian','belarusian','bulgarian','serbian','macedonian','bosnian','montenegrin','rusyn'].includes(input.profile) ? 'cyrillic' : Object.hasOwn(profiles,input.profile) ? input.profile : 'greek',
      source: ['en','fr','de'].includes(language(input.source)) ? language(input.source) : 'en',
      percent: Number.isFinite(Number(input.percent)) ? Math.min(100,Math.max(0,Number(input.percent))) : 20,
      stage: [1,2,3].includes(Number(input.stage)) ? Number(input.stage) : 3,
      seed: String(input.seed ?? 'boulingua-v1')};
  }
  // These are conservative grapheme heuristics, never a pronunciation dictionary.
  // Ambiguous digraphs, final French consonants and English vowels stay original.
  function eligible(word, index, source, profile) {
    const w = word.toLowerCase(), c = w[index], prev = w[index-1] || '', next = w[index+1] || '';
    if (/\p{M}/u.test(next)) return false;
    if (profile==='polish'||profile==='czech') {
      if(source==='fr')return c==='j';
      if(source==='de')return c==='z' && next!=='s' && prev!=='t';
      if(c==='y')return index===0 && vowel.test(next);
      return profile==='polish' && c==='w' && index===0 && /[aeiou]/.test(next) && !['who','whom','whose','whole','two','answer','sword'].includes(w);
    }
    if (profile==='nordic') {
      if(source==='de')return c==='ö';
      if(source==='fr')return 'èê'.includes(c);
      return c==='a' && new Set(['a rabbit','rabbit','rabbits','cat','cats','hat','hats','hatter','had','has','have','having','bank','banks','happy','black','back','hand','hands','man','cap','map','bad','mad','sad','sat','that','than','can','cannot','ran','began','Alice'.toLowerCase()]).has(w);
    }
    if (source === 'en') {
      if (!'bdfgklmnprstvz'.includes(c)) return false;
      if ((c==='t' || c==='p') && next==='h') return false;
      if (c==='t' && /^(ion|ia|ient|ure)/.test(w.slice(index+1))) return false;
      if (c==='s' && (next==='h' || prev==='i' || (vowel.test(prev)&&vowel.test(next)) || !next)) return false;
      if (c==='g') return false; // soft and silent g are too common for a letter rule
      if (c==='k' && next==='n') return false;
      if (c==='b' && (prev==='m'||next==='t')) return false;
      if (c==='n' && next==='g') return false;
      if (c==='l' && /^(k|m|f|d)/.test(next)) return false;
      if (c==='r') return false; // rhoticity and /ɹ/ versus /r/ are not a close match
      if (/(?:^(?:pneum|ps|pt)|^(?:listen|often|whistle|castle|fasten))/.test(w)) return false;
    }
    if (source === 'fr') {
      if (!'abdfgiklmnoprstvzj'.includes(c)) return false;
      if ('bdgpmnprstxz'.includes(c) && index===w.length-1) return false;
      if ('aiom n'.replaceAll(' ','').includes(c) && /[mn]/.test(next) && (!w[index+2] || !vowel.test(w[index+2]))) return false;
      if (c==='n' && (prev==='g' || vowel.test(prev) && !vowel.test(next))) return false;
      if (c==='m' && vowel.test(prev) && !vowel.test(next)) return false;
      if ('aio'.includes(c) && (vowel.test(prev)||vowel.test(next)||/[mn]/.test(next))) return false;
      if (c==='i' && next==='l') return false;
      if (c==='l' && (prev==='i'||w.slice(index-2,index)==='il')) return false;
      if (c==='p' && next==='h') return false;
      if (c==='t' && next==='i') return false;
      if (c==='s' && (vowel.test(prev)&&vowel.test(next))) return false;
      if (c==='g' && /[eéiiy n]/.test(next || ' ')) return false;
      if (c==='r') return false; // French /ʁ/ is not Greek or Cyrillic /r/
    }
    if (source === 'de') {
      if (!'abdfiklmnoprtwö'.includes(c)) return false;
      if ('ai o'.replaceAll(' ','').includes(c) && (vowel.test(prev)||vowel.test(next))) return false;
      if (c==='p' && (next==='h'||next==='f')) return false;
      if (c==='f' && prev==='p') return false;
      if (c==='t' && (next==='h'||next==='i')) return false;
      if (c==='n' && (next==='g'||next==='k')) return false;
      if ((c==='b'||c==='d') && (!next || !vowel.test(next))) return false;
      if (c==='r') return false;
    }
    return true;
  }
  function transform(text, input = {}) {
    const opt = settings(input), profile=profiles[opt.profile];
    let eligibleCount=0, replaced=0, letterCount=0;
    // Tokenise addresses as a whole so URLs and email addresses remain usable.
    const result=String(text).replace(/(?:https?:\/\/|www\.)[^\s<>]+|[\p{L}\p{N}._%+-]+@[\p{L}\p{N}.-]+\.[\p{L}]{2,}|[\p{L}\p{M}]+/gu,(word,offset)=>{
      if (word.includes('@')||word.includes('://')||word.startsWith('www.')) return word;
      return Array.from(word).map((char,i)=>{
        if(letters.test(char))letterCount++;
        const lower=char.toLowerCase();
        if(profile.staged!==false && opt.stage<3 && !(opt.stage===1?'mnt':'mntpkflbd').includes(lower))return char;
        let target=profile.map[lower];
        if (opt.source==='de' && lower==='w' && opt.profile!=='ukrainian' && !target) target=profile.map.v;
        if (!target||target===lower||!eligible(word,i,opt.source,opt.profile))return char;
        eligibleCount++;
        if (hash(`${opt.seed}|${word}|${offset+i}`)/4294967296 >= opt.percent/100) return char;
        if(opt.profile==='greek'&&target==='σ'&&i===word.length-1)target='ς';
        replaced++;
        return char===char.toUpperCase()?target.toUpperCase():target;
      }).join('');
    });
    return {text:result,eligible:eligibleCount,replaced,letters:letterCount};
  }
  const api={version:'0.2.0',profiles,language,settings,transform,hash};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.Scriptbridge=api;
})(typeof globalThis==='undefined'?this:globalThis);
