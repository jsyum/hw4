/**
 * A Gothic reading-room window with the night sky behind it.
 *
 * Drawn here rather than loaded as an image: original geometry, no external
 * files, and the stars twinkle from CSS. Decorative only — hidden from screen
 * readers.
 */

// Fixed positions so the sky doesn't reshuffle on every render.
const STARS: Array<[number, number, number, number]> = [
  // x, y, r, animation-delay (s)
  [28, 42, 1.3, 0], [62, 30, 1.0, 1.4], [96, 55, 1.5, 0.7], [128, 28, 1.1, 2.1],
  [44, 88, 1.2, 1.1], [84, 104, 1.0, 2.6], [118, 86, 1.4, 0.4], [150, 62, 1.1, 1.8],
  [36, 140, 1.0, 2.3], [72, 158, 1.3, 0.9], [112, 148, 1.0, 1.6], [146, 120, 1.2, 3.0],
  [58, 196, 1.1, 0.6], [104, 206, 1.0, 2.0], [140, 182, 1.3, 1.3], [24, 112, 1.0, 2.8],
]

export function StarryWindow({ className = '' }: { className?: string }) {
  return (
    <svg
      className={`starry-window ${className}`}
      viewBox="0 0 180 300"
      aria-hidden
      focusable="false"
    >
      <defs>
        {/* the arch, used to clip the sky */}
        <clipPath id="win-arch">
          <path d="M14 290V96C14 46 46 14 90 14s76 32 76 82v194z" />
        </clipPath>
        <linearGradient id="win-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0b1f3d" />
          <stop offset="55%" stopColor="#12294c" />
          <stop offset="100%" stopColor="#0a1628" />
        </linearGradient>
        <radialGradient id="win-moon">
          <stop offset="0%" stopColor="#f6e6bd" />
          <stop offset="100%" stopColor="#e3c05c" />
        </radialGradient>
        {/* userSpaceOnUse matters: the mullions are straight lines, so their
            object bounding box has zero width and an objectBoundingBox gradient
            cannot be mapped onto them — they simply would not paint. */}
        <linearGradient id="win-frame" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="180" y2="300">
          <stop offset="0%" stopColor="#8b6340" />
          <stop offset="50%" stopColor="#6b4a2f" />
          <stop offset="100%" stopColor="#4e3824" />
        </linearGradient>
        {/* lamplight from the reading room, washing up the glass */}
        <radialGradient id="win-lamp" cx="0.5" cy="1" r="0.75">
          <stop offset="0%" stopColor="#f0c67a" stopOpacity="0.30" />
          <stop offset="55%" stopColor="#f0c67a" stopOpacity="0.09" />
          <stop offset="100%" stopColor="#f0c67a" stopOpacity="0" />
        </radialGradient>
      </defs>

      <g clipPath="url(#win-arch)">
        <rect x="0" y="0" width="180" height="300" fill="url(#win-sky)" />
        <circle cx="128" cy="70" r="15" fill="url(#win-moon)" opacity="0.92" />
        <circle cx="122" cy="64" r="13" fill="#11274a" />
        {STARS.map(([x, y, r, d], i) => (
          <circle
            key={i}
            className="star"
            cx={x}
            cy={y}
            r={r}
            fill="#f0e6d2"
            style={{ animationDelay: `${d}s` }}
          />
        ))}
        {/* lamplight spilling up the glass from the reading room below */}
        <rect x="0" y="120" width="180" height="180" fill="url(#win-lamp)" />
      </g>

      {/* stone surround + mullions */}
      <path
        d="M14 290V96C14 46 46 14 90 14s76 32 76 82v194z"
        fill="none"
        stroke="url(#win-frame)"
        strokeWidth="9"
      />
      <g stroke="url(#win-frame)" strokeWidth="5" opacity="0.95">
        <path d="M90 20v270" />
        <path d="M18 120h144" />
        <path d="M18 200h144" />
      </g>
      {/* sill */}
      <rect x="4" y="286" width="172" height="10" rx="3" fill="#4e3824" />
    </svg>
  )
}
