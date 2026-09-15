// Only presentation: the server has already chosen and persisted the winner.
export async function animateReel(root, caja, winner, reelCard) {
  const track = root.querySelector('#reel-track');
  const viewport = root.querySelector('.reel-viewport');
  if (!track || !viewport) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    track.innerHTML = reelCard(winner);
    track.classList.add('result-state');
    return;
  }
  const pool = caja.items.map(ci=>ci.item);
  const cards = Array.from({length:55},(_,i)=>i===44 ? winner : pool[Math.floor(Math.random()*pool.length)]);
  track.innerHTML = cards.map(item=>reelCard(item)).join('');
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  const winnerCard = track.children[44];
  const target = viewport.clientWidth/2 - (winnerCard.offsetLeft + winnerCard.offsetWidth/2);
  const animation = track.animate([{transform:'translateX(0)'},{transform:`translateX(${target}px)`}],
    {duration:4200,easing:'cubic-bezier(0.05, 0.9, 0.25, 1)',fill:'forwards'});
  await animation.finished;
}
