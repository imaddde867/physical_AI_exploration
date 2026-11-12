// Usage: <div class="q" data-a="1"> <p>..</p> <button>..</button>... <div class="why">..</div></div>
document.querySelectorAll('.q').forEach(q=>{
  const a=+q.dataset.a;
  q.querySelectorAll('button').forEach((b,i)=>b.onclick=()=>{
    if(q.classList.contains('done'))return;
    b.classList.add(i===a?'ok':'bad');
    if(i!==a)q.querySelectorAll('button')[a].classList.add('ok');
    q.classList.add('done');
  });
});
