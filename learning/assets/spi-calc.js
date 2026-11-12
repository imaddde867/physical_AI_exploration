// Best SPI rate not above the request: clk_peri / (CPSDVSR * (1 + SCR)), CPSDVSR even 2..254, SCR 0..255 (RP2040 datasheet, PrimeCell SSP).
// Assumption: the real driver picks the nearest rate not above the request. Print the SPI object on the board to see the true value.
function bestSpi(clk, want){
  let best=0;
  for(let p=2;p<=254;p+=2)for(let s=0;s<=255;s++){const r=clk/(p*(1+s));if(r<=want&&r>best)best=r;}
  return best;
}
const BITS=240*280*16;
function run(){
  const clk=+document.getElementById('clk').value*1e6, want=+document.getElementById('want').value*1e6;
  const r=bestSpi(clk,want), t=BITS/r;
  document.getElementById('out').textContent=
   'actual SPI clock : '+(r/1e6).toFixed(3)+' MHz\nfull frame        : '+(t*1000).toFixed(1)+' ms\nmax full-frame fps: '+(1/t).toFixed(1)+'  (pixel data only)';
}
document.querySelectorAll('.calc input').forEach(i=>i.oninput=run);run();
