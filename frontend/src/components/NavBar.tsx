import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export function NavBar() {
  const { user, ready, signOut } = useAuth()
  const navigate = useNavigate()

  function onSignOut() {
    signOut()
    navigate('/')
  }

  return (
    <header className="nav">
      <div className="nav-inner">
        <NavLink to="/" className="brand">
          <span className="brand-mark">CC</span>
          <span className="brand-text">
            <strong>Campus Customs</strong>
            <small>Yale Bulldog Blue</small>
          </span>
        </NavLink>

        <nav className="nav-links" aria-label="Main">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="nav-account">
          {!ready ? null : user ? (
            <>
              <span className="who" title={user.email}>
                Signed in as <strong>{user.first_name || user.name}</strong>
              </span>
              <button type="button" className="btn ghost" onClick={onSignOut}>
                Log Out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn ghost">
                Log In
              </NavLink>
              <NavLink to="/create-account" className="btn">
                Create Account
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
