/** Shapes returned by the Campus Customs API. These mirror the database columns;
 *  `image_url` and `total_stock` are derived by the backend, everything else is
 *  read straight from the catalogue. */

export interface ProductSummary {
  product_id: string
  name: string
  garment_type: string
  description: string
  /** False when the catalogue holds a build-failure placeholder instead of a
   *  real description. The UI shows a neutral line rather than inventing one. */
  description_recorded: boolean
  colors: string[]
  image_url: string
  price: number
  total_stock: number
}

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductDetail extends ProductSummary {
  search_tags: string[]
  inventory: SizeStock[]
}

/** A product the assistant referred to. Built by the backend from real
 *  catalogue rows, never from the model's text. */
export interface ProductCard {
  product_id: string
  name: string
  price: number
  category: string
  garment_type: string
  description: string
  description_recorded: boolean
  colors: string[]
  image_url: string
  total_stock: number
}

export interface ChatReply {
  reply: string
  products: ProductCard[]
  search_query: string | null
  match_count: number | null
  tools_used: string[]
  /** Which model answered and why — surfaced so the routing is visible. */
  model_used: string | null
  routed_as: string | null
  route_reason: string | null
  error: string | null
}

/** The fields the card component renders. Both a catalogue row (ProductSummary)
 *  and a chat match (ProductCard) satisfy it, so the Products page and the chat
 *  results use the same component and look identical. */
export interface CardProduct {
  product_id: string
  name: string
  description: string
  description_recorded: boolean
  image_url: string
  price: number
  total_stock: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

/** An account as the API exposes it. Note there is no password_hash field —
 *  the backend never sends one. */
export interface PublicUser {
  id: number
  name: string
  first_name: string | null
  last_name: string | null
  email: string
  created_at: string
}

export interface AuthResponse {
  token: string
  user: PublicUser
}

/** What the shopper is looking at. Sent with each chat message so the agent can
 *  resolve "this" and "it". Carries no identity and no product facts — the
 *  backend reads the product from the catalogue using the id. */
export interface PageContext {
  kind: 'home' | 'products' | 'product' | 'other'
  product_id?: string | null
}

export interface ChatHistoryMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  products: ProductCard[]
  created_at: string
}

export interface ProductListResponse {
  total: number
  returned: number
  products: ProductSummary[]
  price_min: number | null
  price_max: number | null
  sort: string
}

export interface CategoryInfo {
  category: string
  count: number
  price_min: number
  price_max: number
}

export interface ProductFilters {
  q?: string
  category?: string
  min_price?: number
  max_price?: number
  sort?: string
}
