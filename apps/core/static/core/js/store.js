const rarity = {COMUN:'consumer', RARO:'milspec', EPICO:'classified', LEGENDARIO:'contraband'};

export function normalizeItem(item) {
  return {id:String(item.id), nombre:item.nombre, descripcion:item.descripcion || '',
    valor:Number(item.valor_estimado), rareza:rarity[item.rareza] || 'consumer', image:item.imagen_url, emoji:'◇'};
}

export function normalizeCase(row) {
  const themes = {
    'Fracture Case': ['#8847ff', 'linear-gradient(135deg, #1a0a2e, #2d1b69)'],
    'Operation Riptide': ['#22d3ee', 'linear-gradient(135deg, #0a1628, #0e3a6b)'],
    'Recoil Case': ['#f59e0b', 'linear-gradient(135deg, #1a0d00, #3d2000)'],
    'Dreams & Nightmares': ['#d32ce6', 'linear-gradient(135deg, #0a0a1a, #1a0a2e)'],
  };
  const [borderColor, gradient] = themes[row.nombre] || ['#d7f36b', 'linear-gradient(135deg, #101411, #202820)'];
  return {id:String(row.id), nombre:row.nombre, descripcion:row.descripcion, precio:Number(row.precio),
    image:row.imagen_url, emoji:'◇', gradient, borderColor,
    items:row.items.map(ci=>({item:normalizeItem(ci.item), probabilidad:Number(ci.probabilidad)}))};
}

export function createState(authenticated) {
  return {page:'cases', cases:[], selectedCase:null, authenticated, balance:0, inventario:[], transactions:[], aperturas:0,
    user:{nombreUsuario:'',email:'',steamUsername:'',fechaRegistro:null},
    filter:'ALL', sortBy:'date', contentsOpen:false, openingState:'idle', wonItem:null,
    loading:true, loadError:'', accountReady:!authenticated, busy:false, requestError:'', profileEditing:false};
}

export function applyAccount(state, account) {
  state.balance = Number(account.wallet.saldo);
  state.user = {nombreUsuario:account.user.username, email:account.user.email,
    steamUsername:account.user.steam_username || '', fechaRegistro:account.user.date_joined};
  state.inventario = account.inventory.map(row=>({id:String(row.id),item:normalizeItem(row.item),estado:row.estado,
    fechaAdquisicion:new Date(row.created_at),cajaOrigen:row.caja_nombre}));
  const kinds = {INICIAL:['BONIFICACION','Bono de bienvenida'],RECARGA:['RECARGA','Recarga de créditos virtuales'],
    DEBITO:['COMPRA_CAJA','Apertura de caja'],VENTA:['VENTA_ITEM','Venta de objeto']};
  state.transactions = account.wallet.transacciones.map(tx=>({id:tx.id,tipo:kinds[tx.tipo]?.[0] || 'RECARGA',
    concepto:kinds[tx.tipo]?.[1] || tx.tipo,monto:Number(tx.monto),saldoAnterior:Number(tx.saldo_anterior),
    saldoPosterior:Number(tx.saldo_posterior),fecha:new Date(tx.created_at)}));
  state.aperturas = account.aperturas;
  state.accountReady = true;
}
