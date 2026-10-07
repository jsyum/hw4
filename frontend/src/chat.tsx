import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { fetchChatHistory, sendChat } from './api'
import { useAuth } from './auth'
import type { ChatMessage, PageContext, ProductCard } from './types'

export interface Turn extends ChatMessage {
  products?: ProductCard[]
}

interface Results {
  products: ProductCard[]
  query: string | null
  matchCount: number | null
}

interface LastRoute {
  model: string
  tier: string
  reason: string
  seconds: number
}

interface ChatState {
  messages: Turn[]
  lastRoute: LastRoute | null
  results: Results | null
  busy: boolean
  open: boolean
  restoring: boolean
  setOpen: (open: boolean) => void
  send: (text: string) => Promise<void>
  clearResults: () => void
}

const GREETING: Turn = {
  role: 'assistant',
  content:
    "Hi! I'm the Campus Customs assistant. Ask me about our products — what we carry, " +
    "prices, colours, or what's in stock in your size.",
}

const Ctx = createContext<ChatState | null>(null)

/** Turn the current route into the context the agent needs to resolve "this". */
function pageContextFrom(pathname: string): PageContext {
  const product = pathname.match(/^\/products\/(.+)$/)
  if (product) return { kind: 'product', product_id: decodeURIComponent(product[1]) }
  if (pathname === '/products') return { kind: 'products' }
  if (pathname === '/') return { kind: 'home' }
  return { kind: 'other' }
}

/**
 * Holds the conversation, the latest search results, and the page the shopper is on.
 *
 * Lives inside the router but above the routed page, so it can read the current
 * route while surviving navigation: clicking a product card unmounts the page,
 * never this provider, and the chat comes back exactly as it was.
 *
 * For a signed-in shopper the conversation is also saved server-side and reloaded
 * here on sign-in. Guests keep theirs in memory only.
 */
export function ChatProvider({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth()
  const { pathname } = useLocation()
  const [messages, setMessages] = useState<Turn[]>([GREETING])
  const [results, setResults] = useState<Results | null>(null)
  const [busy, setBusy] = useState(false)
  const [open, setOpen] = useState(false)
  const [restoring, setRestoring] = useState(false)
  const [lastRoute, setLastRoute] = useState<LastRoute | null>(null)
  const inFlight = useRef(false)
  const loadedFor = useRef<number | null>(null)

  // Restore the saved conversation when a shopper signs in; wipe it on sign-out
  // so the next person at this browser never sees the last one's messages.
  useEffect(() => {
    if (!ready) return
    if (!user) {
      loadedFor.current = null
      setMessages([GREETING])
      setResults(null)
      return
    }
    if (loadedFor.current === user.id) return
    loadedFor.current = user.id
    setRestoring(true)
    fetchChatHistory()
      .then((saved) => {
        if (saved.length === 0) {
          setMessages([GREETING])
          return
        }
        setMessages([
          GREETING,
          ...saved.map((m) => ({
            role: m.role,
            content: m.content,
            products: m.products,
          })),
        ])
      })
      .catch(() => setMessages([GREETING]))
      .finally(() => setRestoring(false))
  }, [ready, user])

  const send = useCallback(
    async (text: string) => {
      const message = text.trim()
      if (!message || inFlight.current) return
      inFlight.current = true
      setBusy(true)
      setMessages((m) => [...m, { role: 'user', content: message }])
      const started = performance.now()
      try {
        const reply = await sendChat(message, pageContextFrom(pathname))
        setLastRoute({
          model: reply.model_used ?? '',
          tier: reply.routed_as ?? '',
          reason: reply.route_reason ?? '',
          seconds: (performance.now() - started) / 1000,
        })
        setMessages((m) => [
          ...m,
          { role: 'assistant', content: reply.reply, products: reply.products },
        ])
        // Only replace the page results when this turn actually found products;
        // a follow-up like "how much is it?" shouldn't wipe the grid.
        if (reply.products.length > 0) {
          setResults({
            products: reply.products,
            query: reply.search_query,
            matchCount: reply.match_count,
          })
        }
      } catch (err) {
        setMessages((m) => [
          ...m,
          {
            role: 'assistant',
            content: `I couldn't reach the shop just now (${
              err instanceof Error ? err.message : String(err)
            }).`,
          },
        ])
      } finally {
        inFlight.current = false
        setBusy(false)
      }
    },
    [pathname],
  )

  const clearResults = useCallback(() => setResults(null), [])

  const value = useMemo(
    () => ({ messages, results, busy, open, restoring, lastRoute, setOpen, send, clearResults }),
    [messages, results, busy, open, restoring, lastRoute, send, clearResults],
  )
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useChat(): ChatState {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useChat must be used inside ChatProvider')
  return ctx
}
