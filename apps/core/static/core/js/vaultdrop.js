import {ApiClient} from './api.js';
import {createState, applyAccount, normalizeCase, normalizeItem} from './store.js';
import {createViews} from './views.js';
import {animateReel} from './reel.js';

const root = document.getElementById('vaultdrop-app');
if (root) start(root);

function start(root) {
  const urls = root.dataset;
  const state = createState(urls.authenticated === 'true');
  const api = new ApiClient(urls, urls.userId || 'guest');
  const views = createViews(state, urls);
  let notice = '';

  function render() {
    root.innerHTML = views.html();
    const box = root.querySelector('.toast-container');
    if (notice) { const text=document.createElement('div');text.className='toast';text.setAttribute('role','status');text.textContent=notice;box.append(text); }
    root.querySelectorAll('[data-sort]').forEach(el=>{el.value=state.sortBy;});
    if (state.busy) root.querySelectorAll('button,input,select,[data-case-id],[data-page]').forEach(el=>{
      el.disabled=true;el.setAttribute('aria-disabled','true');
    });
  }

  async function load() {
    state.loading=true;state.loadError='';render();
    try {
      const [cases,account] = await Promise.all([api.request(urls.casesUrl),state.authenticated ? api.request(urls.accountUrl) : null]);
      state.cases=cases.map(normalizeCase);
      if(account) applyAccount(state,account);
    } catch(error) {state.loadError=error.message;}
    finally {state.loading=false;render();}
  }

  async function mutate(action, message) {
    if(state.busy || !state.accountReady) return;
    state.busy=true;state.requestError='';notice='';render();
    try { const data=await action(); applyAccount(state,data.account);notice=message; }
    catch(error) {state.requestError=error.message;}
    finally {state.busy=false;render();}
  }

  async function openCase() {
    if(state.busy || !state.accountReady || state.openingState!=='idle') return;
    const caja=state.selectedCase;
    if(!state.authenticated) {location.href=urls.loginUrl;return;}
    state.busy=true;state.openingState='requesting';state.requestError='';notice='';render();
    try {
      const data=await api.mutate(`${urls.casesUrl}${caja.id}/abrir/`);
      applyAccount(state,data.account);
      const winner=normalizeItem(data.item);
      state.openingState='spinning';render();
      // A visual failure cannot undo or substitute the already committed result.
      try {await animateReel(root,caja,winner,views.reelCard);} catch(_) { /* show result directly */ }
      state.wonItem=winner;state.openingState='result';
    } catch(error) {state.openingState='idle';state.requestError=error.message;}
    finally {state.busy=false;render();}
  }

  root.addEventListener('error',event=>{
    const img=event.target;
    if(img.tagName==='IMG'&&!img.dataset.fallback){img.dataset.fallback='true';img.src='/static/core/images/item-placeholder.svg';}
  },true);

  root.addEventListener('change',event=>{
    if(event.target.matches('[data-sort]')){state.sortBy=event.target.value;render();}
  });

  root.addEventListener('click',event=>{
    const el=event.target.closest('button,[data-page],[data-case-id]');
    if(!el || state.busy) return;
    if(el.matches('[data-retry]')){load();return;}
    if(el.matches('[data-scroll-cases]')){root.querySelector('.cases-grid')?.scrollIntoView({behavior:'smooth'});return;}
    if(el.dataset.page){state.page=el.dataset.page;state.requestError='';notice='';render();return;}
    if(el.dataset.caseId){state.selectedCase=state.cases.find(c=>c.id===el.dataset.caseId);state.page='opening';state.wonItem=null;state.openingState='idle';state.contentsOpen=false;state.requestError='';render();return;}
    if(el.matches('[data-back]')){state.page='cases';state.requestError='';render();return;}
    if(el.matches('[data-toggle-contents]')){state.contentsOpen=!state.contentsOpen;render();return;}
    if(el.matches('[data-open]')){openCase();return;}
    if(el.matches('[data-reset]')){state.openingState='idle';state.wonItem=null;render();return;}
    if(el.dataset.filter){state.filter=el.dataset.filter;render();return;}
    if(el.dataset.sell){mutate(()=>api.mutate(`${urls.inventoryUrl}${el.dataset.sell}/sell/`),'Objeto vendido.');return;}
    if(el.dataset.send){mutate(()=>api.mutate(`${urls.inventoryUrl}${el.dataset.send}/send/`),'Envío simulado guardado. No se realizó una transferencia a Steam.');return;}
    if(el.dataset.deposit || el.matches('[data-custom-deposit]')){
      const monto=el.dataset.deposit || root.querySelector('[data-custom-amount]').value;
      mutate(()=>api.mutate(urls.depositUrl,{monto}),'Créditos virtuales añadidos.');return;
    }
    if(el.matches('[data-edit]')){state.profileEditing=!state.profileEditing;render();return;}
    if(el.matches('[data-save-profile]')){
      const inputs=[...root.querySelectorAll('.profile-edit input')];
      const body={username:inputs[0].value,email:inputs[1].value,steam_username:inputs[2].value};
      mutate(()=>api.request(urls.profileUrl,{method:'PATCH',body}),'Perfil guardado.');
    }
  });
  root.addEventListener('keydown',event=>{
    if((event.key==='Enter'||event.key===' ')&&event.target.matches('[data-case-id],[data-page]:not(button)')){
      event.preventDefault();event.target.click();
    }
  });
  load();
}
