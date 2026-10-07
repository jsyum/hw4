import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './auth'
import { About } from './pages/About'
import { CreateAccount, LogIn } from './pages/Account'
import { Home } from './pages/Home'
import { ProductDetail } from './pages/ProductDetail'
import { Products } from './pages/Products'
import './theme.css'
import './index.css'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: 'products', element: <Products /> },
      { path: 'products/:productId', element: <ProductDetail /> },
      { path: 'about', element: <About /> },
      { path: 'login', element: <LogIn /> },
      { path: 'create-account', element: <CreateAccount /> },
      { path: '*', element: <Home /> },
    ],
  },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
