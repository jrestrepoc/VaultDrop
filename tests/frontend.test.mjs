import test from 'node:test';
import assert from 'node:assert/strict';
import {readdirSync, readFileSync} from 'node:fs';
import {ApiClient} from '../apps/core/static/core/js/api.js';
import {createState, applyAccount} from '../apps/core/static/core/js/store.js';
import {createViews} from '../apps/core/static/core/js/views.js';

globalThis.gettext=text=>text;
globalThis.interpolate=(format,values)=>format.replace(/%\((\w+)\)s/g,(_,key)=>values[key]);
globalThis.document={cookie:''};
globalThis.location={origin:'http://localhost'};
globalThis.sessionStorage={getItem:()=>null,setItem:()=>{}};

test('network retry reuses operation key and creates no local prize', async()=>{
  const calls=[];
  globalThis.fetch=async(_,options)=>{calls.push(options.headers['Idempotency-Key']);if(calls.length===1)throw Error('offline');return {ok:true,json:async()=>({id:1})};};
  const api=new ApiClient({},'test');
  await assert.rejects(api.mutate('/open/'));
  await api.mutate('/open/');
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
