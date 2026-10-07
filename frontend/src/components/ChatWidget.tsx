import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { money } from '../api'
import { useChat } from '../chat'
import { Bulldog, PawTrail } from './Bulldog'
import type { DogState } from './Bulldog'

/**
 * The reference desk, bottom right.
 *
 * The conversation itself lives in ChatProvider, above the router, so it stays
 * intact when a shopper clicks a product card and navigates to its page. This
 * component is just the view: a log, an input, and small thumbnails of whatever
 * the assistant found.
 */
export function ChatWidget() {
  const { messages, busy, open, restoring, lastRoute, setOpen, send } = useChat()
  const [draft, setDraft] = useState('')

  // The librarian dozes when the desk is quiet, wakes when the panel is open,
  // and pads off to the stacks while he looks something up.
  const dogState: DogState = busy ? 'thinking' : open ? 'awake' : 'sleeping'
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) endRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, open])

  async function onSend(e: React.FormEvent) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || busy) return
    setDraft('')
    await send(text)
  }

  return (
    <>
      <button
        className={`chat-fab${open ? ' is-open' : ' is-asleep'}`}
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-label={open ? 'Close the reference desk' : 'Ask the librarian'}
      >
        {open ? (
          <span className="fab-close" aria-hidden>
            ×
          </span>
        ) : (
          <>
            {/* Zs drift up out of the button while the desk is quiet. Outside the
                SVG so they can rise past the edge of the bell. */}
            <span className="fab-zzz" aria-hidden>
              <span className="z z1">z</span>
              <span className="z z2">z</span>
              <span className="z z3">z</span>
            </span>
            <Bulldog state="sleeping" size={62} title="Ask the librarian" />
          </>
        )}
      </button>

      {open && (
        <section className="chat-panel" aria-label="Shop assistant">
          <header className="chat-head">
            <Bulldog state={dogState} size={42} />
            <div className="chat-head-text">
              <strong>Ask the Librarian</strong>
              <small>Open late. Ask the librarian any time.</small>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close the reference desk">
              ×
            </button>
          </header>

          <div className="chat-log">
            {messages.map((m, i) => (
              <div key={i} className="turn">
                <div className={`bubble ${m.role}`}>{m.content}</div>
                {m.products && m.products.length > 0 && (
                  <ul className="chat-cards">
                    {m.products.map((p) => (
                      <li key={p.product_id}>
                        {/* The panel stays open: the conversation and the page
                            results both live above the router, so navigating
                            away and back loses nothing. */}
                        <Link to={`/products/${p.product_id}`}>
                          <img src={p.image_url} alt="" loading="lazy" />
                          <span className="chat-card-text">
                            <strong>{p.name}</strong>
                            <span className="chat-card-price">
                              {money(p.price)}
                              {p.total_stock === 0 && ' · out of stock'}
                            </span>
                          </span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
            {restoring && <p className="chat-note">Fetching your card from the catalogue…</p>}
            {busy && <PawTrail />}
            <div ref={endRef} />
          </div>

          {lastRoute?.model && (
            /* Makes the model routing visible while the shop is being built.
               Remove this line for a real storefront. */
            <p className="chat-foot">
              answered by{' '}
              <span className={lastRoute.tier === 'fast' ? 'tier-fast' : 'tier-strong'}>
                {lastRoute.model}
              </span>{' '}
              · {lastRoute.reason} · {lastRoute.seconds.toFixed(1)}s
            </p>
          )}

          <form className="chat-input" onSubmit={onSend}>
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Ask the librarian…"
              disabled={busy}
              aria-label="Message"
            />
            <button type="submit" disabled={busy || !draft.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
    </>
  )
}
