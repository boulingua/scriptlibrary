const {chromium}=require('@playwright/test');
const {default:AxeBuilder}=require('@axe-core/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const D=require('../static/js/editions.js'),E=require('../static/js/engine.js'),root=path.resolve(__dirname,'..');
async function settleTransitions(page){
 await page.evaluate(async()=>{
  await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);
  await Promise.all(document.getAnimations().filter(a=>a.effect.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})));
 });
}
async function accessible(page,label,selector){
 await settleTransitions(page);
 const scan=new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']);
 if(selector)scan.include(selector);
 const result=await scan.analyze();
 assert.deepEqual(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),[],label);
}
(async()=>{
 fs.mkdirSync(path.join(root,'tmp'),{recursive:true});
 const browser=await chromium.launch({...(process.env.CHROMIUM ? {executablePath:process.env.CHROMIUM} : {channel:'chromium'}),headless:true,args:[]});
 try{
 const base=process.env.LIBRARY_URL||'http://localhost:1317/scriptlibrary/';
 const context=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await context.newPage();const errors=[],failed=[],consoleErrors=[],requestFailures=[];
 page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});page.on('requestfailed',r=>requestFailures.push({url:r.url(),failure:r.failure()}));
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failed.push(r.url());});
 const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/catalog.json')));
 for(const book of catalog){
  console.log(`Checking ${book.id}`);
  const data=JSON.parse(fs.readFileSync(path.join(root,`data/texts/${book.id}.json`)));
  const paragraphs=data.chapters.flatMap(c=>c.paragraphs);
  await page.goto(base+`books/${book.id}/`);await page.waitForFunction(()=>document.querySelector('#reading-status').textContent.includes('letters changed')).catch(async error=>{const state=await page.evaluate(()=>({readyState:document.readyState,book:document.querySelector('[data-book]')?.dataset.book,engine:typeof Scriptbridge,editions:typeof ScriptlibraryEditions,profiles:document.querySelector('#profile')?.options.length,scripts:[...document.scripts].map(s=>({src:s.src,defer:s.defer})),resources:performance.getEntriesByType('resource').filter(r=>r.name.includes('/js/')).map(r=>({name:r.name,duration:r.duration,responseStatus:r.responseStatus}))}));throw new Error(`${book.id}: ${await page.locator('#reading-status').textContent()}; diagnostics: ${JSON.stringify({state,errors,failed,consoleErrors,requestFailures})}; ${error.message}`);});
  assert.equal(await page.locator('.downloads a[download][href$=".pdf"]').count(),16);
  assert.equal(await page.locator('.learning-notice').count(),1);
  for(const profile of [...Object.keys(E.profiles),'original'])for(const mode of (profile==='original'?['20']:['20','100','progressive'])){
   await page.locator('#mode').selectOption(mode==='progressive'?'progressive':'fixed');
   await page.locator('#profile').selectOption(profile);
   if(profile!=='original'&&mode!=='progressive')await page.locator('#density').fill(mode);
   const actual=await page.locator('[data-paragraph]').allTextContents();
   const expected=paragraphs.map((p,index)=>p.runs.map((r,j)=>E.transform(r.text,{profile,source:book.language,percent:profile==='original'?0:D.percent(mode,index,paragraphs.length),seed:`${book.id}:${p.id}:${j}`}).text).join(''));
   assert.deepEqual(actual,expected,`${book.id}/${profile}/${mode} reader differs from edition engine`);
  }
  await page.locator('#mode').selectOption('fixed');
  await page.locator('#profile').selectOption('cyrillic');await page.locator('#density').fill('55');await page.reload();assert.equal(await page.locator('#density').inputValue(),'55');
  await page.locator('#mode').selectOption('progressive');await page.reload();assert.equal(await page.locator('#mode').inputValue(),'progressive');await page.locator('#original').click();assert.equal(await page.locator('#profile').inputValue(),'original');
  await page.reload();await page.locator('#original').click();assert.equal(await page.locator('#profile').inputValue(),'cyrillic','Resume practice must retain the previous alphabet after an original-view reload');
 }
 // Existing saved records have no lastPractice field. Preserve their alphabet;
 // a legacy original-only record cannot recover an alphabet it never stored.
 await page.evaluate(()=>localStorage.setItem('scriptlibrary:alice',JSON.stringify({profile:'polish',percent:45,mode:'fixed'})));
 await page.goto(base+'books/alice/');assert.equal(await page.locator('#profile').inputValue(),'polish');
 await page.locator('#original').click();await page.reload();await page.locator('#original').click();assert.equal(await page.locator('#profile').inputValue(),'polish');
 await page.goto(base);await page.evaluate(()=>document.fonts.ready);await accessible(page,'Home page in light mode');await page.screenshot({path:path.join(root,'tmp/library-desktop.png'),fullPage:true});
 await page.locator('#dark-mode-toggle').click();assert.match(await page.locator('body').getAttribute('class'),/colorscheme-dark/);await page.waitForFunction(()=>Number(getComputedStyle(document.querySelector('.navigation-title')).color.match(/\d+/)[0])>180);await accessible(page,'Home page in dark mode');await page.screenshot({path:path.join(root,'tmp/library-dark.png'),fullPage:true,animations:'disabled'});await page.locator('#dark-mode-toggle').click();await settleTransitions(page);
 await page.setViewportSize({width:390,height:844});await page.goto(base);await page.screenshot({path:path.join(root,'tmp/library-mobile.png'),fullPage:true});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 for(const cover of await page.locator('.book-cover').all())assert.equal(await cover.evaluate(e=>e.scrollWidth>e.clientWidth),false);
 await page.locator('label[for=menu-toggle]').click();await page.getByRole('link',{name:'How it works',exact:true}).click();assert.match(page.url(),/about\/$/);
 await page.goto(base+'books/verwandlung/');await page.locator('#mode').selectOption('fixed');await page.locator('#profile').selectOption('cyrillic');await page.locator('#density').fill('20');await page.locator('#chapter-1').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(root,'tmp/reader-mobile.png')});
 await page.setViewportSize({width:1440,height:1000});await page.evaluate(()=>window.scrollTo(0,document.querySelector('#chapter-1').getBoundingClientRect().top+scrollY-35));await page.screenshot({path:path.join(root,'tmp/reader-desktop.png')});
 const nojs=await browser.newContext({javaScriptEnabled:false});const plain=await nojs.newPage();await plain.goto(base+'books/alice/');assert.equal(await plain.locator('[data-paragraph]').count(),catalog[0].id==='alice'?JSON.parse(fs.readFileSync(path.join(root,'data/texts/alice.json'))).chapters.flatMap(c=>c.paragraphs).length:0);assert.match(await plain.locator('[data-paragraph]').first().innerText(),/^Alice was beginning/);await nojs.close();
 const automatic=await browser.newContext({colorScheme:'dark'}),autoPage=await automatic.newPage();await autoPage.goto(base+'books/alice/');await autoPage.waitForFunction(()=>document.querySelector('#reading-status').textContent.includes('letters changed'));await accessible(autoPage,'Reader tools under OS dark preference','.reader-tools');
 await autoPage.evaluate(()=>{document.body.classList.remove('colorscheme-light','colorscheme-dark');document.body.classList.add('colorscheme-auto');});await accessible(autoPage,'Reader tools with automatic dark styling','.reader-tools');await automatic.close();
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 console.log('PASS: all 288 reader/edition combinations agree exactly; persisted settings, original view, dark mode, mobile menu, responsive covers, no-JS complete text; home light/dark and automatic-dark reader accessibility; no browser errors or failed requests.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
