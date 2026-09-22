const {chromium}=require('@playwright/test');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const D=require('../static/js/editions.js'),E=require('../static/js/engine.js'),root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try{
 const base=process.env.LIBRARY_URL||'http://localhost:1317/scriptlibrary/';
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[],failed=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failed.push(r.url());});
 const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/catalog.json')));
 for(const book of catalog){
  const data=JSON.parse(fs.readFileSync(path.join(root,`data/texts/${book.id}.json`)));
  const paragraphs=data.chapters.flatMap(c=>c.paragraphs);
  await page.goto(base+`books/${book.id}/`);await page.waitForFunction(()=>document.querySelector('#reading-status').textContent.includes('letters changed'));
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
 }
 await page.goto(base);await page.screenshot({path:path.join(root,'tmp/library-desktop.png'),fullPage:true});
 await page.locator('#dark-mode-toggle').click();assert.match(await page.locator('body').getAttribute('class'),/colorscheme-dark/);await page.waitForFunction(()=>Number(getComputedStyle(document.querySelector('.navigation-title')).color.match(/\d+/)[0])>180);await page.screenshot({path:path.join(root,'tmp/library-dark.png'),fullPage:true,animations:'disabled'});await page.locator('#dark-mode-toggle').click();
 await page.setViewportSize({width:390,height:844});await page.goto(base);await page.screenshot({path:path.join(root,'tmp/library-mobile.png'),fullPage:true});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 for(const cover of await page.locator('.book-cover').all())assert.equal(await cover.evaluate(e=>e.scrollWidth>e.clientWidth),false);
 await page.locator('label[for=menu-toggle]').click();await page.getByRole('link',{name:'How it works',exact:true}).click();assert.match(page.url(),/about\/$/);
 await page.goto(base+'books/verwandlung/');await page.locator('#mode').selectOption('fixed');await page.locator('#profile').selectOption('cyrillic');await page.locator('#density').fill('20');await page.locator('#chapter-1').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(root,'tmp/reader-mobile.png')});
 await page.setViewportSize({width:1440,height:1000});await page.evaluate(()=>window.scrollTo(0,document.querySelector('#chapter-1').getBoundingClientRect().top+scrollY-35));await page.screenshot({path:path.join(root,'tmp/reader-desktop.png')});
 const nojs=await browser.newContext({javaScriptEnabled:false});const plain=await nojs.newPage();await plain.goto(base+'books/alice/');assert.equal(await plain.locator('[data-paragraph]').count(),catalog[0].id==='alice'?JSON.parse(fs.readFileSync(path.join(root,'data/texts/alice.json'))).chapters.flatMap(c=>c.paragraphs).length:0);assert.match(await plain.locator('[data-paragraph]').first().innerText(),/^Alice was beginning/);await nojs.close();
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 console.log('PASS: all 192 reader/edition combinations agree exactly; persisted settings, original view, dark mode, mobile menu, responsive covers, no-JS complete text; no browser errors or failed requests.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
