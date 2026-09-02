(() => {
  const root = document.getElementById('vaultdrop-app');
  if (!root) return;

  const rarezaConfig = {
    consumer: { label: 'Consumer Grade', color: '#b0c3d9', bg: 'rgba(176,195,217,0.12)', glow: 'rgba(176,195,217,0.3)' },
    industrial: { label: 'Industrial Grade', color: '#5e98d9', bg: 'rgba(94,152,217,0.12)', glow: 'rgba(94,152,217,0.4)' },
    milspec: { label: 'Mil-Spec', color: '#4b69ff', bg: 'rgba(75,105,255,0.12)', glow: 'rgba(75,105,255,0.5)' },
    restricted: { label: 'Restricted', color: '#8847ff', bg: 'rgba(136,71,255,0.12)', glow: 'rgba(136,71,255,0.5)' },
    classified: { label: 'Classified', color: '#d32ce6', bg: 'rgba(211,44,230,0.12)', glow: 'rgba(211,44,230,0.6)' },
    covert: { label: 'Covert', color: '#eb4b4b', bg: 'rgba(235,75,75,0.12)', glow: 'rgba(235,75,75,0.7)' },
    contraband: { label: 'Contraband ★', color: '#e4ae39', bg: 'rgba(228,174,57,0.15)', glow: 'rgba(228,174,57,0.8)' },
  };

  const items = [
    { id: 'i1', nombre: 'AK-47 | Redline', descripcion: 'Classic aggressive rifle', valor: 85, rareza: 'classified', emoji: '🔫' },
    { id: 'i2', nombre: 'AWP | Dragon Lore', descripcion: 'Legendary sniper rifle', valor: 850, rareza: 'contraband', emoji: '🐉' },
    { id: 'i3', nombre: 'M4A4 | Howl', descripcion: 'Restricted heavy assault', valor: 320, rareza: 'covert', emoji: '🐺' },
    { id: 'i4', nombre: 'Glock-18 | Fade', descripcion: 'Vibrant fading pistol', valor: 55, rareza: 'restricted', emoji: '🌈' },
    { id: 'i5', nombre: 'Desert Eagle | Blaze', descripcion: 'Fire-tipped magnum', valor: 42, rareza: 'classified', emoji: '🔥' },
    { id: 'i6', nombre: 'Karambit | Doppler', descripcion: 'Curved blade with depth', valor: 280, rareza: 'covert', emoji: '🗡️' },
    { id: 'i7', nombre: 'P250 | Mehndi', descripcion: 'Ornate pattern pistol', valor: 8, rareza: 'industrial', emoji: '🎨' },
    { id: 'i8', nombre: 'USP-S | Kill Confirmed', descripcion: 'Confirmed silenced pistol', valor: 22, rareza: 'milspec', emoji: '💀' },
    { id: 'i9', nombre: 'MP5-SD | Phosphor', descripcion: 'Glowing SMG', valor: 3, rareza: 'consumer', emoji: '⚡' },
    { id: 'i10', nombre: 'Nova | Antique', descripcion: 'Vintage shotgun', valor: 2, rareza: 'consumer', emoji: '🪨' },
    { id: 'i11', nombre: 'MAC-10 | Neon Rider', descripcion: 'Cyberpunk SMG skin', valor: 18, rareza: 'milspec', emoji: '🌙' },
    { id: 'i12', nombre: 'Butterfly Knife | Tiger', descripcion: 'Striped butterfly blade', valor: 190, rareza: 'classified', emoji: '🦋' },
    { id: 'i13', nombre: 'SSG 08 | Blue Spruce', descripcion: 'Icy sniper rifle', valor: 5, rareza: 'industrial', emoji: '❄️' },
    { id: 'i14', nombre: 'FAMAS | Mecha Industries', descripcion: 'Robotic assault rifle', valor: 12, rareza: 'milspec', emoji: '🤖' },
    { id: 'i15', nombre: 'CZ75-Auto | Emerald Quartz', descripcion: 'Crystal green pistol', valor: 28, rareza: 'restricted', emoji: '💎' },
  ];

  const fallbackCases = [
    { id: 'c1', nombre: 'Fracture Case', descripcion: 'High value covert items. Good chance at classified weapons.', precio: 45, emoji: '💥', gradient: 'linear-gradient(135deg, #1a0a2e, #2d1b69)', borderColor: '#8847ff', items: [
      { item: items[1], probabilidad: 0.5 }, { item: items[2], probabilidad: 1.5 }, { item: items[5], probabilidad: 3 }, { item: items[0], probabilidad: 8 }, { item: items[4], probabilidad: 12 }, { item: items[3], probabilidad: 20 }, { item: items[7], probabilidad: 30 }, { item: items[9], probabilidad: 24.5 },
    ] },
    { id: 'c2', nombre: 'Operation Riptide', descripcion: 'Ocean-themed skins. Risk the waves for rare finds.', precio: 25, emoji: '🌊', gradient: 'linear-gradient(135deg, #0a1628, #0e3a6b)', borderColor: '#22d3ee', items: [
      { item: items[2], probabilidad: 0.8 }, { item: items[11], probabilidad: 2.5 }, { item: items[0], probabilidad: 5 }, { item: items[14], probabilidad: 10 }, { item: items[10], probabilidad: 18 }, { item: items[7], probabilidad: 25 }, { item: items[12], probabilidad: 28 }, { item: items[9], probabilidad: 10.7 },
    ] },
    { id: 'c3', nombre: 'Recoil Case', descripcion: 'Entry-level case with balanced rarity distribution.', precio: 12, emoji: '🎯', gradient: 'linear-gradient(135deg, #1a0d00, #3d2000)', borderColor: '#f59e0b', items: [
      { item: items[1], probabilidad: 0.3 }, { item: items[4], probabilidad: 3 }, { item: items[3], probabilidad: 8 }, { item: items[14], probabilidad: 15 }, { item: items[13], probabilidad: 22 }, { item: items[6], probabilidad: 25 }, { item: items[8], probabilidad: 26.7 },
    ] },
    { id: 'c4', nombre: 'Dreams & Nightmares', descripcion: 'Community case with stunning artwork. Very rare drops.', precio: 65, emoji: '🌌', gradient: 'linear-gradient(135deg, #0a0a1a, #1a0a2e)', borderColor: '#d32ce6', items: [
      { item: items[1], probabilidad: 0.2 }, { item: items[5], probabilidad: 1 }, { item: items[11], probabilidad: 3 }, { item: items[0], probabilidad: 6 }, { item: items[4], probabilidad: 12 }, { item: items[10], probabilidad: 20 }, { item: items[7], probabilidad: 27 }, { item: items[9], probabilidad: 30.8 },
    ] },
  ];

  const state = {
    page: 'cases',
    selectedCase: null,
    cases: fallbackCases,
    user: {
      nombreUsuario: root.dataset.username || 'Striker_99',
      email: root.dataset.email || 'striker99@email.com',
      steamUsername: `${root.dataset.username || 'Striker_99'}_Steam`,
      fechaRegistro: new Date('2024-01-15'),
    },
    authenticated: root.dataset.authenticated === 'true',
    balance: Number(root.dataset.balance || 1000),
    transactions: [{
      id: generateId(),
      tipo: 'BONIFICACION',
      monto: 1000,
      saldoAnterior: 0,
      saldoPosterior: Number(root.dataset.balance || 1000),
      concepto: 'Bono de bienvenida',
      fecha: new Date('2024-01-15'),
    }],
    inventario: [],
    aperturas: 0,
    filter: 'ALL',
    sortBy: 'date',
    contentsOpen: false,
    openingState: 'idle',
    wonItem: null,
  };

  function generateId() {
    return Math.random().toString(36).slice(2, 9);
  }

  function fmtCurrency(n) {
    return Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function fmtDate(d) {
    return new Date(d).toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function csrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function rarityKey(rareza) {
    const map = { COMUN: 'consumer', RARO: 'milspec', EPICO: 'classified', LEGENDARIO: 'contraband' };
    return map[rareza] || rareza || 'consumer';
  }

  function normalizeCase(apiCase, index) {
    const fallback = fallbackCases[index % fallbackCases.length];
    return {
      id: String(apiCase.id),
      nombre: apiCase.nombre,
      descripcion: apiCase.descripcion || fallback.descripcion,
      precio: Number(apiCase.precio),
      emoji: fallback.emoji,
      gradient: fallback.gradient,
      borderColor: fallback.borderColor,
      items: (apiCase.items || []).map((ci, i) => ({
        probabilidad: Number(ci.probabilidad),
        item: {
          id: String(ci.item.id),
          nombre: ci.item.nombre,
          descripcion: ci.item.descripcion || fallback.items[i % fallback.items.length].item.descripcion,
          valor: Number(ci.item.valor_estimado || ci.item.valor || 0),
          rareza: rarityKey(ci.item.rareza),
          emoji: fallback.items[i % fallback.items.length].item.emoji,
        },
      })),
    };
  }

  function selectItemByProbability(caseItems) {
    const total = caseItems.reduce((sum, ci) => sum + ci.probabilidad, 0);
    let roll = Math.random() * total;
    for (const ci of caseItems) {
      roll -= ci.probabilidad;
      if (roll <= 0) return ci.item;
    }
    return caseItems[caseItems.length - 1].item;
  }

  function badge(rareza) {
    const cfg = rarezaConfig[rareza];
    return `<span class="rarity-badge" style="background:${cfg.bg};color:${cfg.color};border:1px solid ${cfg.color}40">${cfg.label}</span>`;
  }

  function render() {
    root.innerHTML = `
      <div class="app-shell">
        ${renderNav()}
        <main class="app-main">${renderPage()}</main>
        <footer class="footer">
          <span class="footer-brand">⚡ VAULTDROP</span>
          <span>Academic simulation · Virtual credits only · Not a real gambling platform</span>
          <span>v1.0.0 · SOLID Architecture</span>
        </footer>
        <div class="toast-container"></div>
      </div>`;
    bindEvents();
  }

  function renderNav() {
    const navItems = [
      { id: 'cases', label: 'Cases', icon: '📦' },
      { id: 'inventory', label: 'Inventory', icon: '🎒' },
      { id: 'wallet', label: 'Wallet', icon: '💰' },
      { id: 'profile', label: 'Profile', icon: '👤' },
    ];
    return `
      <nav class="top-nav">
        <div class="logo" data-page="cases">⚡ VAULTDROP</div>
        <div class="nav-links">
          ${navItems.map(item => `<button class="nav-button ${state.page === item.id || (state.page === 'opening' && item.id === 'cases') ? 'active' : ''}" data-page="${item.id}"><span>${item.icon}</span><span>${item.label}</span></button>`).join('')}
        </div>
        <div class="balance-badge" data-page="wallet"><span>¢</span><span class="balance-value">${fmtCurrency(state.balance)}</span></div>
        <div class="user-avatar" data-page="profile">${state.user.nombreUsuario[0].toUpperCase()}</div>
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
    return `
      <section class="section">
        <div class="section-head">
          <h1 class="gradient-text section-title">OPEN CASES</h1>
          <p class="section-copy">Choose a case and test your luck. Virtual credits only.</p>
        </div>
        <div class="cases-grid">
          ${state.cases.map(caja => `
            <article class="case-card card-hover" data-case-id="${caja.id}" style="background:${caja.gradient};border:1px solid ${caja.borderColor}60">
              <div class="case-glow" style="background:${caja.borderColor}20"></div>
              <div class="case-emoji">${caja.emoji}</div>
              <h3 class="case-name">${caja.nombre}</h3>
              <p class="case-description">${caja.descripcion}</p>
              <div class="case-card-foot">
                <div class="mini-items">
                  ${caja.items.slice(0, 4).map(ci => {
                    const cfg = rarezaConfig[ci.item.rareza];
                    return `<div class="mini-item" title="${ci.item.nombre}" style="background:${cfg.bg};border:1px solid ${cfg.color}50">${ci.item.emoji}</div>`;
                  }).join('')}
                  ${caja.items.length > 4 ? `<div class="mini-more">+${caja.items.length - 4}</div>` : ''}
                </div>
                <div class="price-pill">¢${fmtCurrency(caja.precio)}</div>
              </div>
            </article>`).join('')}
        </div>
      </section>`;
  }

  function renderOpening() {
    const caja = state.selectedCase;
    const canOpen = state.balance >= caja.precio;
    const result = state.wonItem;
    const cfg = result ? rarezaConfig[result.rareza] : null;
    return `
      <section class="section opening">
        <button class="back-button" data-back>← Back to Cases</button>
        <div class="selected-case" style="background:${caja.gradient};border:1px solid ${caja.borderColor}60">
          <div style="font-size:48px">${caja.emoji}</div>
          <div><h2>${caja.nombre}</h2><p>${caja.descripcion}</p></div>
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
          ${state.openingState === 'idle' ? `<button class="primary-action" data-open ${canOpen ? '' : 'disabled'}>${canOpen ? `🎲 OPEN CASE — ¢${fmtCurrency(caja.precio)}` : '⚠️ INSUFFICIENT BALANCE'}</button>` : ''}
          ${state.openingState === 'spinning' ? '<button class="primary-action" disabled>⏳ SPINNING...</button>' : ''}
          ${state.openingState === 'result' ? '<button class="primary-action" data-reset>🎲 OPEN AGAIN</button><button class="secondary-action" data-page="inventory">VIEW INVENTORY</button>' : ''}
        </div>
        <div class="case-contents">
          <button class="ghost-button" data-toggle-contents>${state.contentsOpen ? '▲ Hide case contents' : '▼ View case contents'}</button>
          <div class="contents-grid ${state.contentsOpen ? '' : 'hidden'}">
            ${caja.items.slice().sort((a, b) => a.probabilidad - b.probabilidad).map(ci => {
              const c = rarezaConfig[ci.item.rareza];
              return `<div class="content-item" style="background:${c.bg};border:1px solid ${c.color}40">
                <div class="content-item-emoji">${ci.item.emoji}</div>
                <div style="flex:1;min-width:0">
                  <div class="content-item-name">${ci.item.nombre}</div>
                  <div class="content-item-meta"><span style="color:${c.color}">${ci.probabilidad.toFixed(1)}%</span><span style="color:#64748b">¢${fmtCurrency(ci.item.valor)}</span></div>
                </div>
              </div>`;
            }).join('')}
          </div>
        </div>
      </section>`;
  }

  function idleReel(caja) {
    const preview = Array.from({ length: 9 }, (_, i) => caja.items[i % caja.items.length].item);
    return preview.map(item => reelCard(item, 0.25)).join('');
  }

  function reelCard(item, opacity = 1) {
    const c = rarezaConfig[item.rareza];
    return `<div class="reel-card" style="opacity:${opacity};background:radial-gradient(circle at 50% 60%, ${c.glow}20, ${c.bg});border:1px solid ${c.color}50">
      <div class="reel-emoji">${item.emoji}</div><div class="reel-name" style="color:${c.color}">${item.nombre}</div>
    </div>`;
  }

  function renderResult(item) {
    const cfg = rarezaConfig[item.rareza];
    return `<div class="result-card" style="background:radial-gradient(circle at 50% 50%, ${cfg.glow}15, #0f1320);border:1px solid ${cfg.color}60;box-shadow:0 0 40px ${cfg.glow}30">
      <div class="result-emoji">${item.emoji}</div>
      <div style="flex:1">${badge(item.rareza)}<h3 class="result-name">${item.nombre}</h3><p class="result-desc">${item.descripcion}</p></div>
      <div class="result-value"><div class="label-muted">Item value</div><strong style="color:${cfg.color}">¢${fmtCurrency(item.valor)}</strong></div>
    </div>`;
  }

  function renderInventory() {
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
      <div class="inventory-visual" style="background:radial-gradient(circle at 50% 60%, ${c.glow}15, ${c.bg});border-bottom:1px solid ${c.color}20">${ii.item.emoji}</div>
      <div class="inventory-body">${badge(ii.item.rareza)}<div class="inventory-name">${ii.item.nombre}</div>
        <div class="inventory-meta"><div class="inventory-value" style="color:${c.color}">¢${fmtCurrency(ii.item.valor)}</div><div class="state-pill" style="color:${stateColor};background:${stateColor}15">${ii.estado}</div></div>
        <div class="inventory-date">${fmtDate(ii.fechaAdquisicion)} · ${ii.cajaOrigen}</div>
        ${available ? `<div class="inventory-actions"><button class="sell-button" data-sell="${ii.id}">SELL</button><button class="send-button" data-send="${ii.id}">SEND TO STEAM</button></div>` : ''}
      </div>
    </article>`;
  }

  function renderWallet() {
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
        return `<div class="transaction"><div class="tx-icon" style="color:${cfg.color};background:${cfg.color}15;border:1px solid ${cfg.color}40">${cfg.icon}</div><div><div class="tx-title">${tx.concepto}</div><div class="tx-meta">${cfg.label} · ${fmtDate(tx.fecha)}</div></div><div class="tx-amount"><strong style="color:${credit ? '#22d3ee' : '#eb4b4b'}">${credit ? '+' : '-'}¢${fmtCurrency(Math.abs(tx.monto))}</strong><div class="tx-balance">bal: ¢${fmtCurrency(tx.saldoPosterior)}</div></div></div>`;
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
      ['Items Sold', vendidos, '#94a3b8'], ['Sent to Steam', enviados, '#8847ff'], ['Inventory Value', `¢${fmtCurrency(totalValue)}`, '#f59e0b'],
    ];
    return `<section class="section profile">
      <h1 class="gradient-text section-title" style="margin-bottom:28px">PROFILE</h1>
      <div class="profile-card"><div class="profile-avatar">${state.user.nombreUsuario[0].toUpperCase()}</div><div style="flex:1"><h2 class="profile-name">${state.user.nombreUsuario}</h2><div class="profile-email">${state.user.email}</div><div class="profile-facts"><div><span>Steam: </span><strong>${state.user.steamUsername}</strong></div><div><span>Joined: </span>${fmtDate(state.user.fechaRegistro)}</div></div></div><button class="edit-button" data-edit>✏️ Edit</button></div>
      <div class="profile-edit hidden"><h3 class="panel-title">Edit Profile</h3>${['Username','Email','Steam Username'].map((label, i) => `<div class="form-field"><label>${label}</label><input class="text-input" value="${[state.user.nombreUsuario, state.user.email, state.user.steamUsername][i]}"></div>`).join('')}<button class="primary-action">SAVE CHANGES</button></div>
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

  function bindEvents() {
    root.querySelectorAll('[data-page]').forEach(el => el.addEventListener('click', () => {
      state.page = el.dataset.page;
      if (state.page !== 'opening') state.openingState = 'idle';
      render();
    }));
    root.querySelectorAll('[data-case-id]').forEach(el => el.addEventListener('click', () => {
      if (!state.authenticated) {
        window.location.href = root.dataset.registerUrl;
        return;
      }
      state.selectedCase = state.cases.find(c => c.id === el.dataset.caseId);
      state.page = 'opening';
      state.openingState = 'idle';
      state.contentsOpen = false;
      state.wonItem = null;
      render();
    }));
    const back = root.querySelector('[data-back]');
    if (back) back.addEventListener('click', () => { state.page = 'cases'; state.openingState = 'idle'; render(); });
    const toggle = root.querySelector('[data-toggle-contents]');
    if (toggle) toggle.addEventListener('click', () => { state.contentsOpen = !state.contentsOpen; render(); });
    const open = root.querySelector('[data-open]');
    if (open) open.addEventListener('click', openCase);
    const reset = root.querySelector('[data-reset]');
    if (reset) reset.addEventListener('click', resetOpeningState);
    root.querySelectorAll('[data-filter]').forEach(el => el.addEventListener('click', () => { state.filter = el.dataset.filter; render(); }));
    const sort = root.querySelector('[data-sort]');
    if (sort) {
      sort.value = state.sortBy;
      sort.addEventListener('change', () => { state.sortBy = sort.value; render(); });
    }
    root.querySelectorAll('[data-sell]').forEach(el => el.addEventListener('click', () => sellItem(el.dataset.sell)));
    root.querySelectorAll('[data-send]').forEach(el => el.addEventListener('click', () => sendItem(el.dataset.send)));
    root.querySelectorAll('[data-deposit]').forEach(el => el.addEventListener('click', () => deposit(Number(el.dataset.deposit))));
    const customDeposit = root.querySelector('[data-custom-deposit]');
    if (customDeposit) customDeposit.addEventListener('click', () => deposit(Number(root.querySelector('[data-custom-amount]').value)));
    const edit = root.querySelector('[data-edit]');
    if (edit) edit.addEventListener('click', () => root.querySelector('.profile-edit').classList.toggle('hidden'));
  }

  async function openCase() {
    const caja = state.selectedCase;
    if (!caja || state.balance < caja.precio || state.openingState !== 'idle') return;
    let finalWinner = selectItemByProbability(caja.items);

    if (state.authenticated && /^\d+$/.test(caja.id)) {
      try {
        const response = await fetch(`${root.dataset.casesUrl}${caja.id}/abrir/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken(), 'Content-Type': 'application/json' },
          credentials: 'same-origin',
        });
        if (response.ok) {
          const data = await response.json();
          finalWinner = normalizeCase({ ...caja, items: [{ item: data.item, probabilidad: 100 }] }, 0).items[0].item;
        }
      } catch (_) {
        // Keep the local probability result when the API is unavailable.
      }
    }

    state.openingState = 'spinning';
    state.wonItem = null;
    render();

    const reelItems = buildReel(caja, finalWinner);
    const track = root.querySelector('#reel-track');
    track.innerHTML = reelItems.map(item => reelCard(item)).join('');
    requestAnimationFrame(() => {
      track.style.transition = 'none';
      track.style.transform = 'translateX(0)';
      requestAnimationFrame(() => {
        const winnerCard = track.children[44];
        const target = centerReelCard(root.querySelector('.reel-viewport'), winnerCard);
        track.style.transition = 'transform 5s cubic-bezier(0.05, 0.9, 0.25, 1)';
        track.style.transform = `translateX(${target}px)`;
      });
    });

    setTimeout(() => {
      state.openingState = 'result';
      state.wonItem = finalWinner;
      completeOpening(caja, finalWinner);
      showOpeningResult(finalWinner);
      toast(`You got ${finalWinner.nombre}!`, 'success');
    }, 5350);
  }

  function showOpeningResult(item) {
    const cfg = rarezaConfig[item.rareza];
    const highlight = root.querySelector('.center-highlight');
    const resultPanel = root.querySelector('#result-panel');
    const actions = root.querySelector('#opening-actions');
    if (!highlight || !resultPanel || !actions) return;

    highlight.style.borderColor = cfg.color;
    highlight.style.background = `${cfg.glow}10`;
    highlight.style.boxShadow = `0 0 28px ${cfg.glow}70, inset 0 0 20px ${cfg.glow}15`;
    resultPanel.innerHTML = renderResult(item);
    actions.innerHTML = '<button class="primary-action" data-reset>🎲 OPEN AGAIN</button><button class="secondary-action" data-page="inventory">VIEW INVENTORY</button>';
    actions.querySelector('[data-reset]').addEventListener('click', resetOpeningState);
    actions.querySelector('[data-page="inventory"]').addEventListener('click', () => {
      state.page = 'inventory';
      state.openingState = 'idle';
      render();
    });
  }

  function resetOpeningState() {
    state.openingState = 'idle';
    state.wonItem = null;
    render();
  }

  function centerReelCard(viewport, card) {
    const viewportCenter = viewport.clientWidth / 2;
    const cardCenter = card.offsetLeft + card.offsetWidth / 2;
    return viewportCenter - cardCenter;
  }

  function buildReel(caja, winner) {
    const all = caja.items.map(ci => ci.item);
    const reel = [];
    for (let i = 0; i < 44; i += 1) reel.push(all[Math.floor(Math.random() * all.length)]);
    reel.push(winner);
    for (let i = 0; i < 10; i += 1) reel.push(all[Math.floor(Math.random() * all.length)]);
    return reel;
  }

  function completeOpening(caja, item) {
    const prev = state.balance;
    state.balance -= caja.precio;
    state.transactions.push({ id: generateId(), tipo: 'COMPRA_CAJA', monto: caja.precio, saldoAnterior: prev, saldoPosterior: state.balance, concepto: `Opened: ${caja.nombre}`, fecha: new Date() });
    state.inventario.push({ id: generateId(), item, estado: 'DISPONIBLE', fechaAdquisicion: new Date(), cajaOrigen: caja.nombre });
    state.aperturas += 1;
  }

  function sellItem(id) {
    const inv = state.inventario.find(ii => ii.id === id);
    if (!inv) return;
    const prev = state.balance;
    state.balance += inv.item.valor;
    inv.estado = 'VENDIDO';
    state.transactions.push({ id: generateId(), tipo: 'VENTA_ITEM', monto: inv.item.valor, saldoAnterior: prev, saldoPosterior: state.balance, concepto: `Sold: ${inv.item.nombre}`, fecha: new Date() });
    render();
    toast(`Sold ${inv.item.nombre} for ¢${fmtCurrency(inv.item.valor)}`, 'success');
  }

  function sendItem(id) {
    const inv = state.inventario.find(ii => ii.id === id);
    if (!inv) return;
    inv.estado = 'ENVIADO';
    render();
    toast(`${inv.item.nombre} sent to ${state.user.steamUsername} (simulated)`, 'info');
  }

  function deposit(amount) {
    if (!amount || amount <= 0) return;
    const prev = state.balance;
    state.balance += amount;
    state.transactions.push({ id: generateId(), tipo: 'RECARGA', monto: amount, saldoAnterior: prev, saldoPosterior: state.balance, concepto: 'Credit deposit', fecha: new Date() });
    render();
    toast(`+¢${fmtCurrency(amount)} added to your wallet`, 'success');
  }

  function toast(message, type) {
    const box = root.querySelector('.toast-container');
    if (!box) return;
    const colors = type === 'warning' ? ['#1e1200', '#f59e0b50', '#f59e0b'] : type === 'info' ? ['#0e1728', '#22d3ee50', '#22d3ee'] : ['#0f1e0e', '#22c55e50', '#22c55e'];
    const el = document.createElement('div');
    el.className = 'toast';
    el.style.background = colors[0];
    el.style.border = `1px solid ${colors[1]}`;
    el.style.color = colors[2];
    el.textContent = message;
    box.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  async function loadCases() {
    try {
      const response = await fetch(root.dataset.casesUrl, { credentials: 'same-origin' });
      if (!response.ok) return;
      const data = await response.json();
      if (Array.isArray(data) && data.length) {
        state.cases = data.map(normalizeCase).filter(caja => caja.items.length);
        render();
      }
    } catch (_) {
      state.cases = fallbackCases;
    }
  }

  render();
  loadCases();
})();
