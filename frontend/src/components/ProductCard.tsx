import { Link } from 'react-router-dom'
import { money } from '../api'
import type { CardProduct } from '../types'

/** One product tile. Every value shown is read from the catalogue — used both
 *  by the Products page and by the chat's search results. */
export function ProductCard({ product }: { product: CardProduct }) {
  const low = product.total_stock > 0 && product.total_stock < 25

  const out = product.total_stock === 0

  return (
    <Link className={`card${out ? ' is-out' : ''}`} to={`/products/${product.product_id}`}>
      <div className="card-image">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {/* Out of stock, in the language of the building it is sitting in. */}
        {out && (
          <span className="checked-out-stamp" aria-hidden>
            Checked out
            <small>all sizes</small>
          </span>
        )}
      </div>
      <div className="card-body">
        <h3>{product.name}</h3>
        {product.description_recorded ? (
          <p className="card-desc">{product.description}</p>
        ) : (
          /* The catalogue has no real description for this product. Say nothing
             about the garment rather than guessing from its name or photo. */
          <p className="card-desc pending">Details coming soon</p>
        )}
        <div className="card-foot">
          <span className="price">{money(product.price)}</span>
          {out ? (
            <span className="tag out">Checked out</span>
          ) : low ? (
            <span className="tag attention">Low stock</span>
          ) : (
            <span className="tag">In stock</span>
          )}
        </div>
      </div>
    </Link>
  )
}
