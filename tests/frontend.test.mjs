import test from 'node:test';
import assert from 'node:assert/strict';
import {readdirSync, readFileSync} from 'node:fs';
import {ApiClient} from '../apps/core/static/core/js/api.js';
import {createState, applyAccount, upgradeChance, resolveRoute, toggleSelection, toggleAll} from '../apps/core/static/core/js/store.js';
import {createViews} from '../apps/core/static/core/js/views.js';
import {animateReel} from '../apps/core/static/core/js/reel.js';

globalThis.gettext=text=>text;
globalThis.interpolate=(format,values)=>format.replace(/%\((\w+)\)s/g,(_,key)=>values[key]);
globalThis.document={cookie:''};
globalThis.location={origin:'http://localhost'};
globalThis.sessionStorage={getItem:()=>null,setItem:()=>{}};

test('reel spins even with reduced motion and lands on the server prize',async()=>{
  globalThis.matchMedia=()=>({matches:true});
  globalThis.requestAnimationFrame=callback=>callback();
  let frames;
  const track={children:{44:{offsetLeft:1000,offsetWidth:100}},animate:keyframes=>{frames=keyframes;return {finished:Promise.resolve()};}};
  const root={querySelector:selector=>selector==='#reel-track' ? track : {clientWidth:500}};
  await animateReel(root,{items:[{item:{id:'x'}}]},{id:'w'},item=>`[${item.id}]`);
  assert.equal(track.innerHTML.match(/\[.\]/g).length,55);
  assert.equal(track.innerHTML.match(/\[.\]/g)[44],'[w]');
  assert.equal(frames[1].transform,'translateX(-800px)');
});

test('HTTP without randomUUID sends a UUID and reuses it on network retry', async(t)=>{
  const originalCrypto = Object.getOwnPropertyDescriptor(globalThis, 'crypto');
  Object.defineProperty(globalThis, 'crypto', {
    configurable: true,
    value: {getRandomValues: globalThis.crypto.getRandomValues.bind(globalThis.crypto)},
  });
  t.after(() => Object.defineProperty(globalThis, 'crypto', originalCrypto));
  const calls=[];
  globalThis.fetch=async(_,options)=>{calls.push(options.headers['Idempotency-Key']);if(calls.length===1)throw Error('offline');return {ok:true,json:async()=>({id:1})};};
  const api=new ApiClient({},'test');
  await assert.rejects(api.mutate('/open/'));
  await api.mutate('/open/');
  assert.match(calls[0], /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  assert.equal(calls[0],calls[1]);
  await api.mutate('/open/');
  assert.notEqual(calls[1],calls[2]);
});

test('server errors are surfaced, never replaced with a prize',async()=>{
  globalThis.fetch=async()=>({ok:false,status:409,json:async()=>({detail:'Saldo insuficiente'})});
  await assert.rejects(new ApiClient({},'test').mutate('/open/'),/Saldo insuficiente/);
});

test('empty catalog stays empty and account is restored from server',()=>{
  const state=createState(true);
  state.loading=false;
  assert.match(createViews(state,{}).html(),/Todavía no hay cajas/);
  applyAccount(state,{user:{username:'Alice',email:'a@example.test',date_joined:'2026-01-01'},wallet:{saldo:'42.50',transacciones:[]},inventory:[],aperturas:3});
  assert.equal(state.balance,42.5);
  assert.equal(state.aperturas,3);
});

test('rate note shows the reference only when the rate exists',()=>{
  const state=createState(true);state.balance=100;
  const views=createViews(state,{});
  assert.doesNotMatch(views.rateNote(),/COP/);
  state.tasaCop=3000;
  assert.match(views.rateNote(),/300.000 COP/);
  assert.match(views.rateNote(),/Rates By Exchange Rate API/);
});

test('every gettext call exists in the catalog',()=>{
  const folder=new URL('../apps/core/static/core/js/',import.meta.url);
  const source=readdirSync(folder).map(file=>readFileSync(new URL(file,folder),'utf8')).join('');
  const catalog=readFileSync(new URL('../locale/en/LC_MESSAGES/djangojs.po',import.meta.url),'utf8');
  const texts=[...source.matchAll(/gettext\('([^']*)'\)/g)].map(match=>match[1]);
  assert.ok(texts.length>0);
  assert.deepEqual(texts.filter(text=>!catalog.includes(`msgid "${text}"`)),[]);
});

test('interface text goes through the translation catalog',()=>{
  const original=globalThis.gettext;
  globalThis.gettext=text=>`T:${text}`;
  const state=createState(true);state.loading=false;
  const html=createViews(state,{}).html();
  globalThis.gettext=original;
  assert.match(html,/T:Cases/);
  assert.match(html,/T:Todavía no hay cajas/);
});

test('navigation and forms expose their state and labels',()=>{
  const state=createState(true);state.accountReady=true;state.page='profile';state.user.nombreUsuario='Ana';
  const html=createViews(state,{}).html();
  assert.match(html,/aria-current="page" data-page="profile"/);
  assert.match(html,/<label for="profile-field-1">/);
  assert.match(html,/id="profile-field-1" class="text-input" type="email"/);
  assert.match(html,/id="main" tabindex="-1"/);
});

test('admin link appears only for staff',()=>{
  const state=createState(true);state.loading=false;
  assert.doesNotMatch(createViews(state,{}).html(),/Administración/);
  assert.match(createViews(state,{adminUrl:'/admin/'}).html(),/href="\/admin\/">Administración/);
});

test('routes resolve known pages and only existing cases',()=>{
  const cases=[{id:'3',nombre:'C'}];
  assert.deepEqual(resolveRoute('case-3',cases),{caja:cases[0],page:'opening'});
  assert.deepEqual(resolveRoute('case-9',cases),{caja:null,page:'cases'});
  for(const page of ['inventory','upgrade','wallet','profile','history']) assert.equal(resolveRoute(page,cases).page,page);
  assert.equal(resolveRoute('',cases).page,'cases');
  assert.equal(resolveRoute('admin',cases).page,'cases');
});

test('selection toggles one item and all visible items',()=>{
  assert.deepEqual(toggleSelection(['1'],'2'),['1','2']);
  assert.deepEqual(toggleSelection(['1','2'],'1'),['2']);
  assert.deepEqual(toggleAll(['1'],['1','2']),['1','2']);
  assert.deepEqual(toggleAll(['1','2'],['1','2']),[]);
});

test('upgrade chance is proportional, capped and needs a better target',()=>{
  assert.equal(upgradeChance(50,100),50);
  assert.equal(upgradeChance(99,100),80);
  assert.equal(upgradeChance(100,100),0);
  assert.equal(upgradeChance(0,100),0);
});

const pistola={id:1,nombre:'<b>Pistola</b>',imagen_url:'',rareza:'COMUN',valor_estimado:'25.00'};
function cuentaCon(estado){
  return {user:{username:'Ana',email:'a@example.test',date_joined:'2026-01-01'},wallet:{saldo:'10.00',transacciones:[]},aperturas:0,caja_gratis:null,
    inventory:[{id:7,item:pistola,estado,created_at:'2026-01-01',caja_nombre:''}]};
}

test('selection only keeps items that are still available',()=>{
  const state=createState(true);state.selection=['7'];
  applyAccount(state,cuentaCon('DISPONIBLE'));
  assert.deepEqual(state.selection,['7']);
  applyAccount(state,cuentaCon('CONSUMIDO'));
  assert.deepEqual(state.selection,[]);
});

test('inventory offers selection and upgraded items show their origin',()=>{
  const state=createState(true);state.page='inventory';
  applyAccount(state,cuentaCon('DISPONIBLE'));
  const html=createViews(state,{}).html();
  assert.match(html,/data-select="7"/);
  assert.match(html,/data-bulk="VENDIDO" disabled/);
  assert.match(html,/· Mejora/);
  assert.ok(!html.includes('<b>Pistola</b>'));
});

test('upgrade page offers only better targets and enables after choosing one',()=>{
  const state=createState(true);state.page='upgrade';
  applyAccount(state,cuentaCon('DISPONIBLE'));
  state.selection=['7'];
  state.cases=[{items:[{item:{id:'2',nombre:'Mejor',valor:50,rareza:'consumer'}},{item:{id:'3',nombre:'Peor',valor:10,rareza:'consumer'}}]}];
  let html=createViews(state,{}).html();
  assert.match(html,/data-target="2"/);
  assert.doesNotMatch(html,/data-target="3"/);
  assert.match(html,/data-upgrade disabled/);
  state.upgradeTarget='2';
  html=createViews(state,{}).html();
  assert.match(html,/<strong>50,00%<\/strong>/);
  assert.doesNotMatch(html,/data-upgrade disabled/);
});

test('free case banner and ranking escape user content',()=>{
  const state=createState(true);state.loading=false;
  state.cases=[{id:'1',nombre:'C',descripcion:'',precio:5,image:'',emoji:'',gradient:'',borderColor:'',items:[]}];
  state.cajaGratis={id:1,disponible:true};
  state.ranking=[{usuario:'<i>u</i>',item:pistola}];
  const html=createViews(state,{}).html();
  assert.match(html,/daily-banner" data-case-id="1"/);
  assert.ok(!html.includes('<i>u</i>'));
});

test('upgrade result stays hidden while the marker is moving',()=>{
  const state=createState(true);state.page='upgrade';
  applyAccount(state,cuentaCon('DISPONIBLE'));
  state.upgradeResult={exito:true,probabilidad:50,objetivo:'Mejor'};
  state.upgradeState='spinning';
  assert.doesNotMatch(createViews(state,{}).html(),/upgrade-result/);
  state.upgradeState='result';
  assert.match(createViews(state,{}).html(),/upgrade-result won/);
});

test('profile renders while the account is missing',()=>{
  const state=createState(true);state.page='profile';
  assert.match(createViews(state,{}).html(),/profile-avatar">\?</);
});

test('profile content is escaped in HTML',()=>{
  const state=createState(true);state.page='profile';state.user.nombreUsuario='<img src=x onerror=alert(1)>';
  const html=createViews(state,{}).html();
  assert.ok(!html.includes('<img src=x'));
  assert.ok(html.includes('&lt;img'));
});
