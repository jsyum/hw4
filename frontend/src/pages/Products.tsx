import { useEffect, useMemo, useRef, useState } from 'react'
import { fetchCategories, fetchProducts, money } from '../api'
import { ProductCard } from '../components/ProductCard'
import type { CategoryInfo, ProductSummary } from '../types'

const SORTS = [
  { value: 'name', label: 'Name (A–Z)' },
  { value: 'price_asc', label: 'Price: low to high' },
  { value: 'price_desc', label: 'Price: high to low' },
  { value: 'relevance', label: 'Best match' },
]

const PRICE_BANDS = [
  { label: 'Any price', min: undefined, max: undefined },
  { label: 'Under $50', min: undefined, max: 50 },
  { label: '$50 – $70', min: 50, max: 70 },
  { label: '$70 – $90', min: 70, max: 90 },
  { label: '$90 and up', min: 90, max: undefined },
]

export function Products() {
  const [products, setProducts] = useState<ProductSummary[]>([])
  const [total, setTotal] = useState(0)
  const [range, setRange] = useState<{ min: number | null; max: number | null }>({
    min: null,
    max: null,
  })
  const [categories, setCategories] = useState<CategoryInfo[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Filter state
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [band, setBand] = useState(0)
  const [sort, setSort] = useState('name')

  // Debounce typing so a search is one request per pause, not one per keystroke.
  const [debounced, setDebounced] = useState('')
  const firstRun = useRef(true)
  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(search), 250)
    return () => window.clearTimeout(t)
  }, [search])

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => setCategories([]))
  }, [])

  useEffect(() => {
    setLoading(true)
    const { min, max } = PRICE_BANDS[band]
    fetchProducts({
      q: debounced || undefined,
      category: category || undefined,
      min_price: min,
      max_price: max,
      // Typing a search implies you want the best match first, unless you have
      // chosen a sort yourself.
      sort: debounced && sort === 'name' && firstRun.current ? 'relevance' : sort,
    })
      .then((r) => {
        setProducts(r.products)
        setTotal(r.total)
        setRange({ min: r.price_min, max: r.price_max })
        setError(null)
      })
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false))
  }, [debounced, category, band, sort])

  const filtered = useMemo(
    () => Boolean(debounced || category || band !== 0),
    [debounced, category, band],
  )

  function reset() {
    setSearch('')
    setCategory('')
    setBand(0)
    setSort('name')
  }

  return (
    <section>
      <header className="page-head">
        <p className="eyebrow">The collection</p>
        <h1>Products</h1>
        <p className="lede">
          Officially licensed Yale apparel, sized XS through XXL. Stock counts come straight
          from our inventory.
        </p>
      </header>

      <div className="filters" role="search">
        <label className="filter grow">
          <span>Search</span>
          <input
            type="search"
            value={search}
            onChange={(e) => {
              firstRun.current = true
              setSearch(e.target.value)
            }}
            placeholder="hoodie, navy, Berkeley, bulldog…"
          />
        </label>

        <label className="filter">
          <span>Category</span>
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c.category} value={c.category}>
                {c.category} ({c.count})
              </option>
            ))}
          </select>
        </label>

        <label className="filter">
          <span>Price</span>
          <select value={band} onChange={(e) => setBand(Number(e.target.value))}>
            {PRICE_BANDS.map((b, i) => (
              <option key={b.label} value={i}>
                {b.label}
              </option>
            ))}
          </select>
        </label>

        <label className="filter">
          <span>Sort by</span>
          <select
            value={sort}
            onChange={(e) => {
              firstRun.current = false
              setSort(e.target.value)
            }}
          >
            {SORTS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>

        {filtered && (
          <button type="button" className="btn ghost" onClick={reset}>
            Reset
          </button>
        )}
      </div>

      <p className="result-line muted" aria-live="polite">
        {loading
          ? 'Searching…'
          : total === 0
            ? 'No products match those filters.'
            : `${total} ${total === 1 ? 'product' : 'products'}` +
              (range.min != null && range.max != null
                ? range.min === range.max
                  ? ` · ${money(range.min)}`
                  : ` · ${money(range.min)} – ${money(range.max)}`
                : '')}
      </p>

      {error && (
        <p className="error">
          Couldn't load the catalogue: {error}. Is the backend running on port 8000?
        </p>
      )}

      {!loading && total === 0 && !error && (
        <p className="muted">
          Try a different search, or <button type="button" className="linkish" onClick={reset}>clear the filters</button>.
        </p>
      )}

      <div className="grid">
        {products.map((p) => (
          <ProductCard key={p.product_id} product={p} />
        ))}
      </div>
    </section>
  )
}
