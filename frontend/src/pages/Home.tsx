import { Link } from 'react-router-dom'
import { OpenLate } from '../components/OpenLate'
import { StarryWindow } from '../components/Window'

export function Home() {
  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">Yale Bulldog Blue · New Haven</p>
          <h1>Wear the years well.</h1>
          <p className="lede">
            Campus Customs outfits the Yale community — students crossing Cross Campus in
            January, families in the stands at The Game, alumni who still reach for the same
            crewneck a decade on. Officially licensed, built to be worn hard and kept long.
          </p>
          <div className="hero-actions">
            <Link className="btn large" to="/products">
              Browse the stacks
            </Link>
            <Link className="btn ghost large" to="/about">
              About us
            </Link>
          </div>
          <OpenLate />
        </div>
        <div className="hero-window" aria-hidden>
          <StarryWindow />
        </div>
      </section>

      <section className="strip">
        <article>
          <h3>Officially licensed</h3>
          <p>
            Every piece carries Yale marks under licence, so the shield, the wordmark, and
            the bulldog are the real ones — not an approximation.
          </p>
        </article>
        <article>
          <h3>Made for the weather here</h3>
          <p>
            Heavyweight fleece, brushed interiors, and quarter-zips chosen for a New England
            winter rather than a photo shoot.
          </p>
        </article>
        <article>
          <h3>Residential colleges included</h3>
          <p>
            Not just the university marks: the colleges, the teams, and the clubs that make
            up the particular corner of Yale you belong to.
          </p>
        </article>
      </section>

      <section className="band">
        <h2>From the shelf</h2>
        <p>
          Tees, crewnecks, hoodies, quarter-zips, and outerwear — sized XS through XXL, with
          live stock counts on every page so you know what is actually there before you
          commit to it.
        </p>
        <Link className="btn" to="/products">
          Browse everything
        </Link>
      </section>
    </>
  )
}
