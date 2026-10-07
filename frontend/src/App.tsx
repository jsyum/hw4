import { Outlet, ScrollRestoration } from 'react-router-dom'
import { ChatResults } from './components/ChatResults'
import { ChatWidget } from './components/ChatWidget'
import { NavBar } from './components/NavBar'
import { ChatProvider } from './chat'
import { OpenLate } from './components/OpenLate'
import './App.css'

export default function App() {
  return (
    <ChatProvider>
      <Layout />
    </ChatProvider>
  )
}

/** Separate so it can call useChat() beneath the provider App sets up. */
function Layout() {
  return (
    <div className="app">
      <NavBar />
      <main className="page">
        <ChatResults />
        <Outlet />
      </main>
      <footer className="foot">
        <p>Campus Customs · New Haven, Connecticut · Officially licensed Yale apparel</p>
        <OpenLate className="centered" />
      </footer>
      <ChatWidget />
      <ScrollRestoration />
    </div>
  )
}
