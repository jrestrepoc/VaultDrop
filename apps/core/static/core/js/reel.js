// Only presentation: the server has already chosen and persisted the winner.
export async function animateReel(root, caja, winner, reelCard) {
  const track = root.querySelector('#reel-track');
  const viewport = root.querySelector('.reel-viewport');
  if (!track || !viewport) return;
  // Corre siempre: Windows con efectos desactivados pide "reducir movimiento" y dejaba la apertura sin ruleta.
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

// Solo presentacion: el marcador cae en la zona que corresponde al resultado del servidor.
export async function animateUpgrade(root, probabilidad, exito) {
  const marker = root.querySelector('#upgrade-marker');
  if (!marker) return;
  const final = exito ? Math.random() * probabilidad : probabilidad + Math.random() * (100 - probabilidad);
  const left = value => ({left: `${value}%`});
  await marker.animate([left(0), left(100), left(0), left(100), left(final)],
    {duration: 3000, easing: 'cubic-bezier(0.2, 0.6, 0.3, 1)', fill: 'forwards'}).finished;
}
