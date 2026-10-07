/**
 * The reference librarian: an original bulldog illustration, drawn in SVG.
 *
 * Nothing here is traced from or derived from any Yale mark or photograph — it
 * is built from plain ellipses and paths, so the shop carries a bulldog of its
 * own rather than borrowing anyone's logo.
 *
 * Three states: `awake` while you are talking to it, `sleeping` when the desk is
 * quiet, and `thinking` while it looks something up.
 */
export type DogState = 'awake' | 'sleeping' | 'thinking'

export function Bulldog({
  state = 'sleeping',
  size = 44,
  title,
}: {
  state?: DogState
  size?: number
  title?: string
}) {
  const asleep = state === 'sleeping'
  return (
    <svg
      className={`bulldog is-${state}`}
      width={size}
      height={size}
      viewBox="0 0 72 64"
      role="img"
      aria-label={title ?? (asleep ? 'Sleeping bulldog librarian' : 'Bulldog librarian')}
    >
      {/* Rose ears: small, folded, set high and wide — a bulldog's are nothing
          like a round teddy ear, and getting them wrong is what makes a drawing
          read as a bear cub. */}
      <path d="M14 20c-5-4-10-3-11 2s3 9 8 10z" fill="#7a5636" />
      <path d="M58 20c5-4 10-3 11 2s-3 9-8 10z" fill="#7a5636" />
      <path d="M15 23c-3-2-6-1.5-6.5 1.5s1.8 5.5 4.6 6.6z" fill="#5d4027" />
      <path d="M57 23c3-2 6-1.5 6.5 1.5s-1.8 5.5-4.6 6.6z" fill="#5d4027" />

      {/* Head: distinctly wider than tall, flat across the top. */}
      <path
        d="M36 9c16 0 26 7 26 19 0 13-11 22-26 22S10 41 10 28C10 16 20 9 36 9z"
        fill="#b08756"
      />
      {/* the wrinkled brow */}
      <path d="M26 21c3.5-3 7-3.6 9.6-2.4" stroke="#8f6a40" strokeWidth="2.6" fill="none" strokeLinecap="round" />
      <path d="M46 21c-3.5-3-7-3.6-9.6-2.4" stroke="#8f6a40" strokeWidth="2.6" fill="none" strokeLinecap="round" />
      <path d="M33 14.5c1.8-1.2 4.2-1.2 6 0" stroke="#8f6a40" strokeWidth="2.2" fill="none" strokeLinecap="round" />

      {/* Jowls: wide, heavy, hanging past the jaw. */}
      <ellipse cx="22" cy="42" rx="12" ry="10.5" fill="#d8b689" />
      <ellipse cx="50" cy="42" rx="12" ry="10.5" fill="#d8b689" />
      <ellipse cx="36" cy="38" rx="15" ry="11" fill="#e0c097" />

      {/* flat wide nose */}
      <path d="M31 31.5h10c1.4 0 2.4 1.1 2.4 2.4 0 2.2-2.8 4.1-7.4 4.1s-7.4-1.9-7.4-4.1c0-1.3 1-2.4 2.4-2.4z" fill="#2a1a10" />
      <path d="M36 38v3.5" stroke="#2a1a10" strokeWidth="2" strokeLinecap="round" />
      <path d="M36 41.5c-3.4 0-5.6-1.6-5.6-3.4M36 41.5c3.4 0 5.6-1.6 5.6-3.4"
            stroke="#2a1a10" strokeWidth="2" fill="none" strokeLinecap="round" />
      {/* underbite */}
      <rect x="31.6" y="43.4" width="3.4" height="3.4" rx="1" fill="#f6f1e6" />
      <rect x="37" y="43.4" width="3.4" height="3.4" rx="1" fill="#f6f1e6" />

      {/* eyes */}
      {asleep ? (
        <>
          <path d="M22 26.5c2.6 2.8 6.4 2.8 9 0" stroke="#2a1a10" strokeWidth="2.2" fill="none" strokeLinecap="round" />
          <path d="M41 26.5c2.6 2.8 6.4 2.8 9 0" stroke="#2a1a10" strokeWidth="2.2" fill="none" strokeLinecap="round" />
        </>
      ) : (
        <>
          <circle cx="26.5" cy="25.5" r="3.6" fill="#f6f1e6" />
          <circle cx="45.5" cy="25.5" r="3.6" fill="#f6f1e6" />
          <circle className="dog-pupil" cx={state === 'thinking' ? 27.6 : 26.9} cy="26" r="2" fill="#13233a" />
          <circle className="dog-pupil" cx={state === 'thinking' ? 46.6 : 45.9} cy="26" r="2" fill="#13233a" />
        </>
      )}

      {/* brass reading glasses, resting on the brow */}
      <g className="dog-glasses" fill="none" stroke="#c9a227" strokeWidth="2">
        <circle cx="26.5" cy="25.5" r="7.2" />
        <circle cx="45.5" cy="25.5" r="7.2" />
        <path d="M33.7 25.5h4.6" strokeLinecap="round" />
        <path d="M19.3 24c-2.8-.9-4.6-.4-5.6.8" strokeLinecap="round" />
        <path d="M52.7 24c2.8-.9 4.6-.4 5.6.8" strokeLinecap="round" />
      </g>

      {/* collar + brass tag */}
      <path d="M18 50c6 4.5 30 4.5 36 0" stroke="#14396b" strokeWidth="5.5" fill="none" strokeLinecap="round" />
      <circle cx="36" cy="54.5" r="3.6" fill="#c9a227" stroke="#8a6c1f" strokeWidth="0.8" />

      {asleep && (
        <g className="dog-zzz" fill="#e3c05c" fontFamily="var(--font-display)" fontWeight="700">
          <text x="56" y="16" fontSize="11">z</text>
          <text x="64" y="8" fontSize="7.5">z</text>
        </g>
      )}
    </svg>
  )
}

/** A single paw print. Used for the walking "thinking" indicator. */
export function Paw({ size = 16, className = '' }: { size?: number; className?: string }) {
  return (
    <svg className={`paw ${className}`} width={size} height={size} viewBox="0 0 24 24" aria-hidden>
      <g fill="currentColor">
        <ellipse cx="12" cy="16" rx="5.4" ry="4.6" />
        <ellipse cx="5.6" cy="9.8" rx="2.3" ry="2.9" />
        <ellipse cx="10" cy="6.8" rx="2.2" ry="3" />
        <ellipse cx="14.8" cy="7.1" rx="2.2" ry="3" />
        <ellipse cx="18.8" cy="10.6" rx="2.2" ry="2.8" />
      </g>
    </svg>
  )
}

/** Paw prints walking across the desk while the librarian looks something up. */
export function PawTrail() {
  return (
    <span className="paw-trail" role="status" aria-label="Looking that up">
      {[0, 1, 2, 3].map((i) => (
        <Paw key={i} size={14} className={`paw-step step-${i}`} />
      ))}
    </span>
  )
}
