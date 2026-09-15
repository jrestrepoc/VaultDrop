export class ApiError extends Error {
  constructor(message, status = 0) { super(message); this.status = status; }
}

function errorMessage(data) {
  if (typeof data === 'string') return data;
  return data?.detail || data?.error || Object.values(data || {}).flat().join(' ') || 'No se pudo completar la operación.';
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
      throw new ApiError('No hay conexión. Reintenta la misma acción; no se cobrará dos veces.');
    }
    let data;
    try { data = await response.json(); } catch (_) { throw new ApiError('El servidor no devolvió una respuesta válida. Reintenta la misma acción.', response.status >= 500 ? response.status : 0); }
    if (!response.ok) throw new ApiError(errorMessage(data), response.status);
    return data;
  }

  async mutate(url, body = {}) {
    const signature = JSON.stringify([url, body]);
    const key = this.pending.get(signature) || crypto.randomUUID();
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
