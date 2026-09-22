const {test}=require('node:test'),assert=require('node:assert/strict');
const D=require('../static/js/editions.js');
test('progressive density reaches both endpoints without resetting at chapters',()=>{
 const values=Array.from({length:101},(_,i)=>D.percent('progressive',i,101));
 assert.equal(values[0],20);assert.equal(values.at(-1),100);assert.equal(values[50],60);
 assert.ok(values.every((v,i)=>i===0||v>values[i-1]));
 assert.equal(D.percent('20',80,101),20);assert.equal(D.percent('100',0,101),100);
 assert.equal(D.percent('progressive',0,1),20);assert.throws(()=>D.percent('bad',0,10));
});
