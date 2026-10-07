import { useChat } from '../chat'
import { ProductCard } from './ProductCard'

/**
 * Products the assistant found, rendered in the main area of the page.
 *
 * The cards come from the chat API's `products` array — real catalogue rows the
 * agent's search tool returned — not from anything parsed out of its reply. They
 * use the same card component as the Products page, so they are clickable and
 * open the full product page exactly as a browsed card does.
 */
export function ChatResults() {
  const { results, clearResults } = useChat()
  if (!results || results.products.length === 0) return null

  const { products, query, matchCount } = results
  const more = typeof matchCount === 'number' && matchCount > products.length

  return (
    <section className="chat-results" aria-label="Products from your chat">
      <header className="chat-results-head">
        <div>
          <p className="eyebrow">From your chat</p>
          <h2>
            {query ? <>Matches for “{query}”</> : 'Matching products'}
          </h2>
          <p className="muted">
            {more
              ? `Showing ${products.length} of ${matchCount} products in the catalogue.`
              : `${products.length} ${products.length === 1 ? 'product' : 'products'}.`}
          </p>
        </div>
        <button type="button" className="btn ghost" onClick={clearResults}>
          Clear
        </button>
      </header>
      <div className="grid">
        {products.map((p) => (
          <ProductCard key={p.product_id} product={p} />
        ))}
      </div>
    </section>
  )
}
