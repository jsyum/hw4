import type {
  AuthResponse,
  ChatHistoryMessage,
  ChatReply,
  PageContext,
  CategoryInfo,
  ProductDetail,
  ProductFilters,
  ProductListResponse,
  PublicUser,
} from './types'

const BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') || ''

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

/** The catalogue, filtered and sorted by the backend.
 *
 *  Filtering happens in SQL via the same `db.query_products` the chatbot's search
 *  tool calls, so the page and the assistant always agree about what is in a
 *  category and which item is cheapest. */
export function fetchProducts(filters: ProductFilters = {}): Promise<ProductListResponse> {
  const params = new URLSearchParams()
  if (filters.q?.trim()) params.set('q', filters.q.trim())
  if (filters.category) params.set('category', filters.category)
  if (filters.min_price != null) params.set('min_price', String(filters.min_price))
  if (filters.max_price != null) params.set('max_price', String(filters.max_price))
  if (filters.sort) params.set('sort', filters.sort)
  const qs = params.toString()
  return get<ProductListResponse>(`/api/products${qs ? `?${qs}` : ''}`)
}

export function fetchCategories(): Promise<CategoryInfo[]> {
  return get<CategoryInfo[]>('/api/categories')
}

export function fetchProduct(productId: string): Promise<ProductDetail> {
  return get<ProductDetail>(`/api/products/${encodeURIComponent(productId)}`)
}

/** Send a shopper message to the PydanticAI agent behind FastAPI.
 *
 *  The session token goes in the Authorization header and is the only thing that
 *  identifies the shopper — no user id or email is ever sent in the body, so a
 *  tampered request cannot claim to be someone else. `page` carries only a route
 *  kind and a product id; the backend looks the product up itself. */
export async function sendChat(message: string, page?: PageContext): Promise<ChatReply> {
  const token = storedToken()
  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, page: page ?? null }),
  })
  if (!res.ok) throw new Error(await errorMessage(res))
  return res.json()
}

/** A signed-in shopper's saved conversation. Scoped by the token on the server. */
export async function fetchChatHistory(): Promise<ChatHistoryMessage[]> {
  const token = storedToken()
  if (!token) return []
  const res = await fetch(`${BASE}/api/chat/history`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) return []
  const data = (await res.json()) as { messages: ChatHistoryMessage[] }
  return data.messages ?? []
}

/** Prices come from the database as numbers; format only at the edge. */
export function money(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}


// ---------------------------------------------------------------------------
// Accounts
// ---------------------------------------------------------------------------

const TOKEN_KEY = 'cc_token'

export function storedToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function storeToken(token: string | null) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // private browsing: the session just won't survive a reload
  }
}

/** FastAPI puts a plain string in `detail` for our HTTPExceptions and a list of
 *  objects for validation errors. Turn either into one readable sentence. */
async function errorMessage(res: Response): Promise<string> {
  let detail: unknown
  try {
    detail = (await res.json()).detail
  } catch {
    return `Something went wrong (HTTP ${res.status}).`
  }
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const msgs = detail.map((d) => String((d as { msg?: string }).msg || '').replace(/^Value error, /, ''))
    return msgs.filter(Boolean).join(' ') || `Something went wrong (HTTP ${res.status}).`
  }
  return `Something went wrong (HTTP ${res.status}).`
}

async function postAuth(path: string, body: unknown): Promise<AuthResponse> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await errorMessage(res))
  return res.json()
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return postAuth('/api/auth/login', { email, password })
}

export function signup(input: {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}): Promise<AuthResponse> {
  return postAuth('/api/auth/signup', input)
}

/** Restore a session on page load. Returns null if the token is gone or expired. */
export async function fetchMe(token: string): Promise<PublicUser | null> {
  const res = await fetch(`${BASE}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) return null
  return res.json()
}
