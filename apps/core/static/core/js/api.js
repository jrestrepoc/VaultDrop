export class ApiError extends Error {
  constructor(message, status = 0) { super(message); this.status = status; }
}

function errorMessage(data) {
  if (typeof data === 'string') return data;
  return data?.detail || data?.error || Object.values(data || {}).flat().join(' ') || gettext('No se pudo completar la operación.');
}

function operationKey() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();

  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
  return [hex.slice(0, 8), hex.slice(8, 12), hex.slice(12, 16), hex.slice(16, 20), hex.slice(20)].join('-');
}

export class ApiClient {
  constructor(urls, userId) {
    this.urls = urls;
    this.pending = new Map();
    this.storageKey = `vaultdrop:pending:${userId}`;
    try { this.pending = new Map(JSON.parse(sessionStorage.getItem(this.storageKey) || '[]')); } catch (_) { /* storage optional */ }
  }

  persist() {
    try { sessionStorage.setItem(this.storageKey, JSON.stringify([...this.pending])); } catch (_) { /* storage optional */ }
  }

  async request(url, {method = 'GET', body, key} = {}) {
    let response;
    const csrf = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || '';
    try {
      response = await fetch(url, {
        method, credentials: 'same-origin', cache: 'no-store',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': decodeURIComponent(csrf), ...(key ? {'Idempotency-Key': key} : {})},
        ...(body === undefined ? {} : {body: JSON.stringify(body)}),
      });
    } catch (_) {
      throw new ApiError(gettext('No hay conexión. Reintenta la misma acción; no se cobrará dos veces.'));
    }
    let data;
    try { data = await response.json(); } catch (_) { throw new ApiError(gettext('El servidor no devolvió una respuesta válida. Reintenta la misma acción.'), response.status >= 500 ? response.status : 0); }
    if (!response.ok) throw new ApiError(errorMessage(data), response.status);
    return data;
  }

  async mutate(url, body = {}) {
    const signature = JSON.stringify([url, body]);
    const key = this.pending.get(signature) || operationKey();
    this.pending.set(signature, key);
    this.persist();
    try {
      const data = await this.request(url, {method:'POST', body, key});
      this.pending.delete(signature);
      this.persist();
      return data;
    } catch (error) {
      if (error.status >= 400 && error.status < 500) { this.pending.delete(signature); this.persist(); }
      throw error;
    }
  }
}
