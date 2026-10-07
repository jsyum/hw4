import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, money } from '../api'
import type { ProductDetail as Detail } from '../types'

export function ProductDetail() {
  const { productId = '' } = useParams()
  const [product, setProduct] = useState<Detail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetchProduct(productId)
      .then(setProduct)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false))
  }, [productId])

  if (loading) return <p className="muted">Loading…</p>
  if (error || !product) {
    return (
      <section className="prose">
        <h1>Product not found</h1>
        <p className="muted">We don't have a product with the id “{productId}”.</p>
        <Link className="btn" to="/products">
          Back to products
        </Link>
      </section>
    )
  }

  const inStock = product.inventory.filter((s) => s.quantity > 0)

  return (
    <article className="detail">
      <nav className="crumbs">
        <Link to="/products">Products</Link> <span aria-hidden>/</span> {product.name}
      </nav>

      <div className="detail-grid">
        <div className="detail-image">
          <img src={product.image_url} alt={product.name} />
          {product.total_stock === 0 && (
            <span className="checked-out-stamp" aria-hidden>
              Checked out
              <small>all sizes</small>
            </span>
          )}
        </div>

        <div className="detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="detail-price"><span className="price">{money(product.price)}</span></p>
          {product.description_recorded ? (
            <p className="detail-desc">{product.description}</p>
          ) : (
            <p className="detail-desc pending">
              Details coming soon — we don't have a description for this one yet.
            </p>
          )}

          <h2>Sizes</h2>
          <table className="sizes">
            <thead>
              <tr>
                <th scope="col">Size</th>
                <th scope="col">Availability</th>
              </tr>
            </thead>
            <tbody>
              {product.inventory.map((s) => (
                <tr key={s.size} className={s.quantity === 0 ? 'row-out' : undefined}>
                  <th scope="row">{s.size}</th>
                  <td>
                    {s.quantity === 0 ? (
                      <span className="tag out">Checked out</span>
                    ) : (
                      <>
                        <span className={s.quantity < 5 ? 'tag attention' : 'tag'}>
                          {s.quantity} in stock
                        </span>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <p className="muted total-line">
            {product.total_stock} units across {inStock.length} of {product.inventory.length} sizes.
          </p>

          <h2>Colours</h2>
          {product.colors.length > 0 ? (
            <ul className="chips">
              {product.colors.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          ) : (
            /* Three catalogue rows have an empty colours array. Saying so beats
               guessing a colour from the photo or the product name. */
            <p className="muted">Our catalogue doesn't list colours for this item.</p>
          )}

          {product.search_tags.length > 0 && (
            <>
              <h2>Details</h2>
              <ul className="chips quiet">
                {product.search_tags.map((t) => (
                  <li key={t}>{t}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
    </article>
  )
}
