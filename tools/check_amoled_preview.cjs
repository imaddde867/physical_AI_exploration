// Exercise the standalone page's actual script with a minimal DOM, offline.
// This checks pixels and controls, not browser layout or physical panel behavior.
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const elements = {};
for (const id of ['face','mood','time','closed','play','stamp']) elements[id] = {value:'', checked:false};
elements.mood.value = 'neutral'; elements.time.value = '0';
let image, now=0, nextFrame=0;
const callbacks=new Map();
function advance(ms) {
    now += ms;
    const pending=[...callbacks.values()];
    callbacks.clear();
    pending.forEach(callback=>callback(now));
}
elements.face.getContext = () => ({putImageData:data => {image=data;}});
elements.face.setAttribute = (k,v) => {elements.face[k]=v;};
elements.mood.add = () => {};
const context = {document:{getElementById:id=>elements[id]}, atob:s=>Buffer.from(s,'base64').toString('binary'),
    Uint8ClampedArray, ImageData:class {constructor(data,w,h){this.data=data;this.width=w;this.height=h;}},
    Option:class {}, performance:{now:()=>now},
    requestAnimationFrame:callback=>{const id=++nextFrame;callbacks.set(id,callback);return id;},
    cancelAnimationFrame:id=>callbacks.delete(id), console};
vm.createContext(context);
const html = fs.readFileSync(process.argv[2], 'utf8');
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], context);
assert.equal(elements.face['aria-label'], 'MacDesk Buddy neutral face');
const hashes=[];
for (const face of ['neutral','happy','sad','sleepy','surprised','thinking']) {
    elements.mood.value=face;
    for (const ms of [0,4000]) {
        elements.time.value=String(ms); elements.time.oninput();
        hashes.push(crypto.createHash('sha256').update(image.data).digest('hex'));
    }
}
elements.time.value='4135'; elements.time.oninput();
assert.equal(elements.face['aria-label'],'MacDesk Buddy thinking face');
elements.closed.checked=true; elements.closed.onchange();
assert.equal(elements.face['aria-label'],'MacDesk Buddy thinking blinking face');
// Run the page's real scheduled tick(), not just its button handler.
elements.closed.checked=false; elements.closed.onchange();
elements.time.value='0'; elements.time.oninput();
elements.play.onclick(); assert.equal(elements.play.textContent,'Pause');
assert.equal(callbacks.size,1);
function at(ms, blinking) {
    assert.equal(Number(elements.time.value),ms);
    assert.equal(elements.face['aria-label'],`MacDesk Buddy thinking${blinking?' blinking':''} face`);
    assert.equal(callbacks.size,1);
}
advance(3999); at(3999,false);
advance(1); at(4000,true);
advance(134); at(4134,true);
advance(1); at(4135,false);
advance(4865); at(9000,true);
advance(135); at(9135,false);
advance(2864); at(11999,false);
advance(1); at(0,false);
advance(250); at(250,false);
elements.play.onclick(); assert.equal(elements.play.textContent,'Play fixed loop');
assert.equal(callbacks.size,0);
advance(5000); assert.equal(Number(elements.time.value),250);
elements.play.onclick(); advance(100); at(350,false);
// A pause/resume before the next paint must not leave two RAF chains.
elements.play.onclick(); elements.play.onclick();
assert.equal(callbacks.size,1);
advance(100); at(450,false);
// Scrubbing cancels playback and resets the resume origin.
elements.time.value='8999'; elements.time.oninput();
assert.equal(elements.play.textContent,'Play fixed loop');
assert.equal(callbacks.size,0);
advance(1000); assert.equal(Number(elements.time.value),8999);
elements.play.onclick(); advance(1); at(9000,true);
console.log(JSON.stringify(hashes));
