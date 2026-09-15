  const rarezaConfig = {
    consumer: { label: 'Consumer Grade', color: '#b0c3d9', bg: 'rgba(176,195,217,0.12)', glow: 'rgba(176,195,217,0.3)' },
    industrial: { label: 'Industrial Grade', color: '#5e98d9', bg: 'rgba(94,152,217,0.12)', glow: 'rgba(94,152,217,0.4)' },
    milspec: { label: 'Mil-Spec', color: '#4b69ff', bg: 'rgba(75,105,255,0.12)', glow: 'rgba(75,105,255,0.5)' },
    restricted: { label: 'Restricted', color: '#8847ff', bg: 'rgba(136,71,255,0.12)', glow: 'rgba(136,71,255,0.5)' },
    classified: { label: 'Classified', color: '#d32ce6', bg: 'rgba(211,44,230,0.12)', glow: 'rgba(211,44,230,0.6)' },
    covert: { label: 'Covert', color: '#eb4b4b', bg: 'rgba(235,75,75,0.12)', glow: 'rgba(235,75,75,0.7)' },
    contraband: { label: 'Contraband ★', color: '#e4ae39', bg: 'rgba(228,174,57,0.15)', glow: 'rgba(228,174,57,0.8)' },
  };


const IMAGE_PLACEHOLDER = '/static/core/images/item-placeholder.svg';
function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char])); }
function fmtCurrency(n) {return Number(n).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});}
function fmtDate(d) {return d ? new Date(d).toLocaleDateString('es-CO') : '—';}
function imageTag(name, src, loading='lazy') {
  let safe=IMAGE_PLACEHOLDER;
  try {const url=new URL(src || IMAGE_PLACEHOLDER,location.origin);if(url.origin===location.origin || url.protocol==='https:') safe=url.href;} catch(_) {}
  return `<img src="${escapeHtml(safe)}" alt="${escapeHtml(name)}" loading="${loading}" decoding="async">`;
}
function badge(rareza) {
  const cfg=rarezaConfig[rareza] || rarezaConfig.consumer;
  return `<span class="rarity-badge" style="background:${cfg.bg};color:${cfg.color};border:1px solid ${cfg.color}40">${cfg.label}</span>`;
}

export function createViews(state, urls) {
  const root = {dataset:urls};
  function renderNav() {
    const navItems = [
      { id: 'cases', label: 'Cases', icon: '📦' },
      { id: 'inventory', label: 'Inventory', icon: '🎒' },
      { id: 'wallet', label: 'Wallet', icon: '💰' },
      { id: 'profile', label: 'Profile', icon: '👤' },
    ];
    return `
      <nav class="top-nav">
        <div class="logo" role="button" tabindex="0" data-page="cases">⚡ VAULTDROP</div>
        <div class="nav-links">
          ${navItems.map(item => `<button class="nav-button ${state.page === item.id || (state.page === 'opening' && item.id === 'cases') ? 'active' : ''}" data-page="${item.id}"><span>${item.icon}</span><span>${item.label}</span></button>`).join('')}
        </div>
        ${state.authenticated ? `<div class="balance-badge" role="button" tabindex="0" data-page="wallet"><span>¢</span><span class="balance-value">${state.accountReady ? fmtCurrency(state.balance) : '…'}</span></div><div class="user-avatar" role="button" tabindex="0" data-page="profile">${escapeHtml((state.user.nombreUsuario[0] || '?').toUpperCase())}</div>` : `<a class="auth-nav-link" href="${root.dataset.loginUrl}">Ingresar</a>`}
      </nav>`;
  }

  function renderPage() {
    if (state.page === 'opening' && state.selectedCase) return renderOpening();
    if (state.page === 'inventory') return renderInventory();
    if (state.page === 'wallet') return renderWallet();
    if (state.page === 'profile') return renderProfile();
    return renderCases();
  }

  function renderCases() {
    if (state.loading) return '<section class="section empty-state" role="status">Cargando catálogo...</section>';
    if (state.loadError) return '<section class="section empty-state"><p>'+escapeHtml(state.loadError)+'</p><button class="primary-action" data-retry>Reintentar</button></section>';
    if (!state.cases.length) return '<section class="section empty-state">Todavía no hay cajas publicadas.</section>';
    const items = state.cases.flatMap(c=>c.items.map(ci=>ci.item));
    const featured = items.find(i=>i.nombre==='AK-47 | Redline') || items[0];
    return `
      <section class="section">
        <div class="catalog-hero">
          <div class="hero-copy"><span class="eyebrow">VAULTDROP / CURATED ARMORY</span><h1>Find the drop<br><em>worth chasing.</em></h1><p>Explora cajas con skins de armas inspiradas en loadouts reales. Créditos virtuales, emoción de apertura.</p><div class="hero-actions"><button class="primary-action" data-scroll-cases>EXPLORE CASES <span>↓</span></button><span class="hero-meta">${new Set(items.map(i=>i.id)).size} items · ${state.cases.length} collections</span></div></div>
          <div class="hero-visual"><div class="hero-orbit"></div>${imageTag(featured?.nombre || 'Colección', featured?.image, 'eager')}<div class="hero-tag">SIMULADOR ACADÉMICO</div><div class="hero-caption"><span>FEATURED DROP</span><strong>${escapeHtml(featured?.nombre || 'Colección')}</strong><small>${featured ? '¢' + fmtCurrency(featured.valor) : ''}</small></div></div>
        </div>
        <div class="section-head catalog-heading"><div><span class="eyebrow">THE ARMORY</span><h2 class="section-title">Open a collection</h2><p class="section-copy">Every case hides a different path to your next loadout.</p></div><div class="catalog-stat"><strong>100%</strong><span>virtual credits</span></div></div>
        <div class="cases-grid">
          ${state.cases.map(caja => `
            <article class="case-card card-hover" role="button" tabindex="0" data-case-id="${caja.id}" style="background:${caja.gradient};border:1px solid ${caja.borderColor}60">
              <div class="case-glow" style="background:${caja.borderColor}20"></div>
              <div class="case-visual">${imageTag(caja.nombre, caja.image)}<span class="case-index">0${state.cases.indexOf(caja) + 1}</span><span class="case-emoji">${caja.emoji}</span></div>
              <div class="case-info"><div class="case-kicker">COLLECTION / ${state.cases.indexOf(caja) + 1}</div><h3 class="case-name">${escapeHtml(caja.nombre)}</h3>
              <p class="case-description">${escapeHtml(caja.descripcion)}</p>
              <div class="case-card-foot">
                <div class="mini-items">
                  ${caja.items.slice(0, 4).map(ci => {
                    const cfg = rarezaConfig[ci.item.rareza];
                    return `<div class="mini-item" title="${escapeHtml(ci.item.nombre)}" style="background:${cfg.bg};border:1px solid ${cfg.color}50">${imageTag(ci.item.nombre, ci.item.image)}</div>`;
                  }).join('')}
                  ${caja.items.length > 4 ? `<div class="mini-more">+${caja.items.length - 4}</div>` : ''}
                </div>
                <div class="price-pill">¢${fmtCurrency(caja.precio)}</div>
              </div></div>
            </article>`).join('')}
        </div>
      </section>`;
  }

  function renderOpening() {
    const caja = state.selectedCase;
    const canOpen = state.accountReady && state.balance >= caja.precio && caja.items.length > 0;
    const result = state.wonItem;
    const cfg = result ? rarezaConfig[result.rareza] : null;
    return `
      <section class="section opening">
        <button class="back-button" data-back>← Back to Cases</button>
        <div class="selected-case" style="background:${caja.gradient};border:1px solid ${caja.borderColor}60">
          <div class="selected-case-visual">${imageTag(caja.nombre, caja.image)}</div>
          <div><h2>${escapeHtml(caja.nombre)}</h2><p>${escapeHtml(caja.descripcion)}</p></div>
          <div class="selected-case-price">
            <div class="label-muted">Case price</div>
            <div class="big-price">¢${fmtCurrency(caja.precio)}</div>
            <div class="label-muted">Balance: ¢${fmtCurrency(state.balance)}</div>
          </div>
        </div>
        <div class="reel-window">
          <div class="center-highlight" ${cfg ? `style="border-color:${cfg.color};background:${cfg.glow}10;box-shadow:0 0 28px ${cfg.glow}70, inset 0 0 20px ${cfg.glow}15"` : ''}></div>
          <div class="reel-fade left"></div><div class="reel-fade right"></div>
          <div class="reel-viewport"><div class="reel-track ${state.wonItem ? 'result-state' : ''}" id="reel-track">${state.wonItem ? reelCard(state.wonItem, 1) : idleReel(caja)}</div></div>
        </div>
        <div id="result-panel">${result ? renderResult(result) : ''}</div>
        <div class="action-row" id="opening-actions">
          ${!state.authenticated ? '<a class="primary-action" href="'+root.dataset.loginUrl+'">Iniciar sesión para abrir</a><a class="secondary-action" href="'+root.dataset.registerUrl+'">Crear cuenta</a>' : ''}
          ${state.openingState === 'requesting' ? '<button class="primary-action" disabled>Confirmando apertura...</button>' : ''}
          ${state.openingState === 'idle' && state.authenticated ? `<button class="primary-action" data-open ${canOpen ? '' : 'disabled'}>${canOpen ? `🎲 OPEN CASE — ¢${fmtCurrency(caja.precio)}` : '⚠️ INSUFFICIENT BALANCE'}</button>` : ''}
          ${state.openingState === 'spinning' ? '<button class="primary-action" disabled>⏳ SPINNING...</button>' : ''}
          ${state.openingState === 'result' ? '<button class="primary-action" data-reset>🎲 OPEN AGAIN</button><button class="secondary-action" data-page="inventory">VIEW INVENTORY</button>' : ''}
        </div>
        <div class="case-contents">
          <button class="ghost-button" data-toggle-contents>${state.contentsOpen ? '▲ Hide case contents' : '▼ View case contents'}</button>
          <div class="contents-grid ${state.contentsOpen ? '' : 'hidden'}">
            ${caja.items.slice().sort((a, b) => a.probabilidad - b.probabilidad).map(ci => {
              const c = rarezaConfig[ci.item.rareza];
              return `<div class="content-item" style="background:${c.bg};border:1px solid ${c.color}40">
                <div class="content-item-visual">${imageTag(ci.item.nombre, ci.item.image)}</div>
                <div style="flex:1;min-width:0">
                  <div class="content-item-name">${escapeHtml(ci.item.nombre)}</div>
                  <div class="content-item-meta"><span style="color:${c.color}">${ci.probabilidad.toFixed(1)}%</span><span style="color:#64748b">¢${fmtCurrency(ci.item.valor)}</span></div>
                </div>
              </div>`;
            }).join('')}
          </div>
        </div>
      </section>`;
  }

  function idleReel(caja) {
    if (!caja.items.length) return '';
    const preview = Array.from({ length: 9 }, (_, i) => caja.items[i % caja.items.length].item);
    return preview.map(item => reelCard(item, 0.25)).join('');
  }

  function reelCard(item, opacity = 1) {
    const c = rarezaConfig[item.rareza];
    return `<div class="reel-card" style="opacity:${opacity};background:radial-gradient(circle at 50% 60%, ${c.glow}20, ${c.bg});border:1px solid ${c.color}50">
      <div class="reel-visual">${imageTag(item.nombre, item.image, 'eager')}<span class="reel-emoji">${item.emoji}</span></div><div class="reel-name" style="color:${c.color}">${escapeHtml(item.nombre)}</div>
    </div>`;
  }

  function renderResult(item) {
    const cfg = rarezaConfig[item.rareza];
    return `<div class="result-card" style="background:radial-gradient(circle at 50% 50%, ${cfg.glow}15, #0f1320);border:1px solid ${cfg.color}60;box-shadow:0 0 40px ${cfg.glow}30">
      <div class="result-visual">${imageTag(item.nombre, item.image, 'eager')}<span class="result-emoji">${item.emoji}</span></div>
      <div style="flex:1">${badge(item.rareza)}<h3 class="result-name">${escapeHtml(item.nombre)}</h3><p class="result-desc">${escapeHtml(item.descripcion)}</p></div>
      <div class="result-value"><div class="label-muted">Item value</div><strong style="color:${cfg.color}">¢${fmtCurrency(item.valor)}</strong></div>
    </div>`;
  }

  function renderInventory() {
    if (!state.authenticated) return renderProfile();
    const filtered = state.inventario
      .filter(ii => state.filter === 'ALL' || ii.estado === state.filter)
      .slice()
      .sort((a, b) => {
        if (state.sortBy === 'value') return b.item.valor - a.item.valor;
        if (state.sortBy === 'rarity') return ['consumer','industrial','milspec','restricted','classified','covert','contraband'].indexOf(b.item.rareza) - ['consumer','industrial','milspec','restricted','classified','covert','contraband'].indexOf(a.item.rareza);
        return b.fechaAdquisicion - a.fechaAdquisicion;
      });
    const total = state.inventario.filter(ii => ii.estado === 'DISPONIBLE').reduce((s, ii) => s + ii.item.valor, 0);
    return `<section class="section">
      <div class="toolbar-head">
        <div><h1 class="gradient-text section-title">INVENTORY</h1><p class="section-copy">${state.inventario.length} items · <span style="color:#f59e0b">¢${fmtCurrency(total)} available</span></p></div>
        <div class="filter-row">
          ${['ALL','DISPONIBLE','VENDIDO','ENVIADO'].map(f => `<button class="filter-button ${state.filter === f ? 'active' : ''}" data-filter="${f}">${f}</button>`).join('')}
          <select class="sort-select" data-sort><option value="date">Sort: Date</option><option value="value">Sort: Value</option><option value="rarity">Sort: Rarity</option></select>
        </div>
      </div>
      ${filtered.length === 0 ? '<div class="empty-state"><div class="empty-icon">📦</div><div class="empty-title">No items found</div><div class="empty-copy">Open some cases to fill your inventory</div></div>' : `<div class="inventory-grid">${filtered.map(renderInventoryItem).join('')}</div>`}
    </section>`;
  }

  function renderInventoryItem(ii) {
    const c = rarezaConfig[ii.item.rareza];
    const available = ii.estado === 'DISPONIBLE';
    const stateColor = ii.estado === 'DISPONIBLE' ? '#22d3ee' : ii.estado === 'VENDIDO' ? '#f59e0b' : '#8847ff';
    return `<article class="inventory-card ${available ? '' : 'dimmed'}" style="border:1px solid ${available ? c.color + '40' : '#1e2d4a'}">
      <div class="inventory-visual" style="background:radial-gradient(circle at 50% 60%, ${c.glow}15, ${c.bg});border-bottom:1px solid ${c.color}20">${imageTag(ii.item.nombre, ii.item.image)}<span>${ii.item.emoji}</span></div>
      <div class="inventory-body">${badge(ii.item.rareza)}<div class="inventory-name">${escapeHtml(ii.item.nombre)}</div>
        <div class="inventory-meta"><div class="inventory-value" style="color:${c.color}">¢${fmtCurrency(ii.item.valor)}</div><div class="state-pill" style="color:${stateColor};background:${stateColor}15">${ii.estado}</div></div>
        <div class="inventory-date">${fmtDate(ii.fechaAdquisicion)} · ${escapeHtml(ii.cajaOrigen)}</div>
        ${available ? `<div class="inventory-actions"><button class="sell-button" data-sell="${ii.id}">SELL</button><button class="send-button" data-send="${ii.id}">SIMULAR ENVÍO</button></div>` : ''}
      </div>
    </article>`;
  }

  function renderWallet() {
    if (!state.authenticated) return renderProfile();
    const txConfig = {
      RECARGA: { icon: '↑', color: '#22d3ee', label: 'Deposit' },
      COMPRA_CAJA: { icon: '↓', color: '#eb4b4b', label: 'Case Purchase' },
      VENTA_ITEM: { icon: '↑', color: '#22d3ee', label: 'Item Sale' },
      BONIFICACION: { icon: '★', color: '#f59e0b', label: 'Bonus' },
    };
    return `<section class="section narrow">
      <h1 class="gradient-text section-title" style="margin-bottom:28px">WALLET</h1>
      <div class="wallet-balance"><div class="wallet-label">AVAILABLE BALANCE</div><div class="wallet-amount">¢${fmtCurrency(state.balance)}</div><div class="wallet-note">Virtual credits · Not redeemable for real money</div></div>
      <div class="panel"><h3 class="panel-title">ADD CREDITS</h3><div class="deposit-row">${[100,250,500,1000,2500].map(v => `<button class="amount-button" data-deposit="${v}">¢${v}</button>`).join('')}</div>
        <div class="custom-deposit"><input class="text-input" type="number" min="1" placeholder="Custom amount..." data-custom-amount><button class="cyan-action" data-custom-deposit>+ ADD CREDITS</button></div>
      </div>
      <h3 class="panel-title">TRANSACTION HISTORY</h3>
      <div class="transactions">${state.transactions.slice().reverse().map(tx => {
        const cfg = txConfig[tx.tipo];
        const credit = tx.tipo !== 'COMPRA_CAJA';
        return `<div class="transaction"><div class="tx-icon" style="color:${cfg.color};background:${cfg.color}15;border:1px solid ${cfg.color}40">${cfg.icon}</div><div><div class="tx-title">${escapeHtml(tx.concepto)}</div><div class="tx-meta">${cfg.label} · ${fmtDate(tx.fecha)}</div></div><div class="tx-amount"><strong style="color:${credit ? '#22d3ee' : '#eb4b4b'}">${credit ? '+' : '-'}¢${fmtCurrency(Math.abs(tx.monto))}</strong><div class="tx-balance">bal: ¢${fmtCurrency(tx.saldoPosterior)}</div></div></div>`;
      }).join('')}</div>
    </section>`;
  }

  function renderProfile() {
    if (!state.authenticated) {
      return `<section class="section narrow">
        <div class="auth-card">
          <h1 class="gradient-text auth-title">PROFILE</h1>
          <p class="auth-subtitle">Inicia sesión o crea una cuenta para consultar tu perfil.</p>
          <div class="action-row">
            <a class="primary-action" href="${root.dataset.loginUrl}">LOGIN</a>
            <a class="secondary-action" href="${root.dataset.registerUrl}">REGISTER</a>
          </div>
        </div>
      </section>`;
    }
    const disponibles = state.inventario.filter(ii => ii.estado === 'DISPONIBLE').length;
    const vendidos = state.inventario.filter(ii => ii.estado === 'VENDIDO').length;
    const enviados = state.inventario.filter(ii => ii.estado === 'ENVIADO').length;
    const totalValue = state.inventario.filter(ii => ii.estado === 'DISPONIBLE').reduce((s, ii) => s + ii.item.valor, 0);
    const stats = [
      ['Balance', `¢${fmtCurrency(state.balance)}`, '#f59e0b'], ['Cases Opened', state.aperturas, '#22d3ee'], ['Items (Active)', disponibles, '#22d3ee'],
      ['Items Sold', vendidos, '#94a3b8'], ['Envíos simulados', enviados, '#8847ff'], ['Inventory Value', `¢${fmtCurrency(totalValue)}`, '#f59e0b'],
    ];
    return `<section class="section profile">
      <h1 class="gradient-text section-title" style="margin-bottom:28px">PROFILE</h1>
      <div class="profile-card"><div class="profile-avatar">${state.user.nombreUsuario[0].toUpperCase()}</div><div style="flex:1"><h2 class="profile-name">${escapeHtml(state.user.nombreUsuario)}</h2><div class="profile-email">${escapeHtml(state.user.email)}</div><div class="profile-facts"><div><span>Steam: </span><strong>${escapeHtml(state.user.steamUsername || 'Sin configurar')}</strong></div><div><span>Joined: </span>${fmtDate(state.user.fechaRegistro)}</div></div></div><button class="edit-button" data-edit>✏️ Edit</button></div>
      <div class="profile-edit ${state.profileEditing ? '' : 'hidden'}"><h3 class="panel-title">Edit Profile</h3>${['Username','Email','Steam Username'].map((label, i) => `<div class="form-field"><label>${label}</label><input class="text-input" value="${escapeHtml([state.user.nombreUsuario, state.user.email, state.user.steamUsername][i])}"></div>`).join('')}<button class="primary-action" data-save-profile>SAVE CHANGES</button></div>
      <div class="stats-grid">${stats.map(s => `<div class="stat-card"><div class="stat-value" style="color:${s[2]}">${s[1]}</div><div class="stat-label">${s[0]}</div></div>`).join('')}</div>
      ${renderRarityBreakdown()}
    </section>`;
  }

  function renderRarityBreakdown() {
    if (!state.inventario.length) return '';
    const counts = {};
    state.inventario.forEach(ii => { counts[ii.item.rareza] = (counts[ii.item.rareza] || 0) + 1; });
    return `<div class="rarity-breakdown"><h3 class="panel-title">RARITY BREAKDOWN</h3>${Object.entries(counts).map(([key, count]) => {
      const cfg = rarezaConfig[key];
      const pct = Math.round((count / state.inventario.length) * 100);
      return `<div class="rarity-row"><div class="rarity-row-head"><span style="color:${cfg.color}">${cfg.label}</span><span style="color:#475569;font-family:'JetBrains Mono',monospace">${count} (${pct}%)</span></div><div class="rarity-bar"><div class="rarity-fill" style="width:${pct}%;background:${cfg.color};box-shadow:0 0 8px ${cfg.glow}"></div></div></div>`;
    }).join('')}</div>`;
  }


  function html() {
    return `<div class="app-shell">${renderNav()}<main class="app-main">
      ${state.requestError ? '<div class="request-error" role="alert">'+escapeHtml(state.requestError)+'</div>' : ''}
      ${state.loadError && state.page !== 'cases' ? '<div class="request-error" role="alert">'+escapeHtml(state.loadError)+' <button data-retry>Reintentar carga</button></div>' : ''}
      ${renderPage()}</main><footer class="footer"><span class="footer-brand">⚡ VAULTDROP</span><span>Simulador académico · Créditos virtuales · Sin dinero real</span></footer><div class="toast-container"></div></div>`;
  }
  return {html, reelCard};
}
