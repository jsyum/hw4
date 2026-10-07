import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { fetchMe, storeToken, storedToken } from './api'
import type { AuthResponse, PublicUser } from './types'

interface AuthState {
  user: PublicUser | null
  ready: boolean
  signIn: (result: AuthResponse) => void
  signOut: () => void
}

const Ctx = createContext<AuthState | null>(null)

/** Holds the signed-in user for the whole app.
 *  The token lives in localStorage so a reload keeps you signed in; the user
 *  object is re-fetched from /api/auth/me rather than trusted from storage. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<PublicUser | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const token = storedToken()
    if (!token) {
      setReady(true)
      return
    }
    fetchMe(token)
      .then((u) => {
        if (!u) storeToken(null)
        setUser(u)
      })
      .finally(() => setReady(true))
  }, [])

  const signIn = useCallback((result: AuthResponse) => {
    storeToken(result.token)
    setUser(result.user)
  }, [])

  const signOut = useCallback(() => {
    storeToken(null)
    setUser(null)
  }, [])

  const value = useMemo(() => ({ user, ready, signIn, signOut }), [user, ready, signIn, signOut])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
