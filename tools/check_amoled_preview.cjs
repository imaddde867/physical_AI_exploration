// Exercise the standalone page's actual script with a minimal DOM, offline.
// This checks pixels and controls, not browser layout or physical panel behavior.
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const elements = {};
for (const id of ['face','mood','time','closed','play','stamp']) elements[id] = {value:'', checked:false};
elements.mood.value = 'neutral'; elements.time.value = '0';
let image;
elements.face.getContext = () => ({putImageData:data => {image=data;}});
elements.face.setAttribute = (k,v) => {elements.face[k]=v;};
elements.mood.add = () => {};
const context = {document:{getElementById:id=>elements[id]}, atob:s=>Buffer.from(s,'base64').toString('binary'),
    Uint8ClampedArray, ImageData:class {constructor(data,w,h){this.data=data;this.width=w;this.height=h;}},
    Option:class {}, performance:{now:()=>0}, requestAnimationFrame:()=>{}, console};
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
elements.play.onclick(); assert.equal(elements.play.textContent,'Pause');
elements.time.oninput(); assert.equal(elements.play.textContent,'Play fixed loop');
console.log(JSON.stringify(hashes));
