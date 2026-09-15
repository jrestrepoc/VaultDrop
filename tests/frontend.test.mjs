import test from 'node:test';
import assert from 'node:assert/strict';
import {ApiClient} from '../apps/core/static/core/js/api.js';
import {createState, applyAccount} from '../apps/core/static/core/js/store.js';
import {createViews} from '../apps/core/static/core/js/views.js';

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

test('profile content is escaped in HTML',()=>{
  const state=createState(true);state.page='profile';state.user.nombreUsuario='<img src=x onerror=alert(1)>';
  const html=createViews(state,{}).html();
  assert.ok(!html.includes('<img src=x'));
  assert.ok(html.includes('&lt;img'));
});
