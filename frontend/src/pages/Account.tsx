import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { login, signup } from '../api'
import { useAuth } from '../auth'

/** Shared chrome for the two account forms. */
function Shell({
  title,
  blurb,
  children,
  footer,
}: {
  title: string
  blurb: string
  children: React.ReactNode
  footer: React.ReactNode
}) {
  return (
    <section className="prose narrow">
      <p className="eyebrow">Account</p>
      <h1>{title}</h1>
      <p className="lede">{blurb}</p>
      {children}
      <p className="muted">{footer}</p>
    </section>
  )
}

export function LogIn() {
  const { user, signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/" replace />

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      signIn(await login(email.trim(), password))
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Shell
      title="Log In"
      blurb="Sign in to your Campus Customs account."
      footer={<>No account yet? <Link to="/create-account">Create one</Link>.</>}
    >
      <form className="account-form" onSubmit={onSubmit} noValidate>
        {error && <p className="error" role="alert">{error}</p>}
        <label>
          Email
          <input
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={busy}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={busy}
          />
        </label>
        <button className="btn" type="submit" disabled={busy || !email || !password}>
          {busy ? 'Signing in…' : 'Log In'}
        </button>
      </form>
    </Shell>
  )
}

export function CreateAccount() {
  const { user, signIn } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/" replace />

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }))

  // Checked here for an instant message, and again by the backend, which is
  // what actually decides.
  const mismatch =
    form.confirm_password.length > 0 && form.password !== form.confirm_password
  const complete = Object.values(form).every((v) => v.trim().length > 0)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (mismatch) {
      setError('Passwords do not match.')
      return
    }
    setBusy(true)
    try {
      signIn(await signup({ ...form, email: form.email.trim() }))
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Shell
      title="Create Account"
      blurb="Make an account to keep your details and your chat history with the shop assistant."
      footer={<>Already have one? <Link to="/login">Log in</Link>.</>}
    >
      <form className="account-form" onSubmit={onSubmit} noValidate>
        {error && <p className="error" role="alert">{error}</p>}
        <div className="field-row">
          <label>
            First name
            <input required value={form.first_name} onChange={set('first_name')} disabled={busy} />
          </label>
          <label>
            Last name
            <input required value={form.last_name} onChange={set('last_name')} disabled={busy} />
          </label>
        </div>
        <label>
          Email
          <input
            type="email"
            autoComplete="email"
            required
            value={form.email}
            onChange={set('email')}
            disabled={busy}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="new-password"
            required
            value={form.password}
            onChange={set('password')}
            disabled={busy}
          />
          <small className="hint">At least 8 characters.</small>
        </label>
        <label>
          Confirm password
          <input
            type="password"
            autoComplete="new-password"
            required
            value={form.confirm_password}
            onChange={set('confirm_password')}
            disabled={busy}
            aria-invalid={mismatch || undefined}
          />
          {mismatch && <small className="hint bad">Passwords do not match.</small>}
        </label>
        <button className="btn" type="submit" disabled={busy || !complete || mismatch}>
          {busy ? 'Creating account…' : 'Create Account'}
        </button>
      </form>
    </Shell>
  )
}
