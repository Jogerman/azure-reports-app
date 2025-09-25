// frontend/src/App.jsx - VERSIÓN FINAL CORREGIDA
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';

// Páginas
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import ReportView from './pages/ReportView';
import History from './pages/History';
import Storage from './pages/Storage';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import MicrosoftCallback from './pages/MicrosoftCallback';

// Componentes
import Layout from './components/common/Layout';
import PrivateRoute from './components/auth/PrivateRoute';

// Configuración React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
    },
    mutations: {
      retry: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              {/* Rutas públicas */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/auth/callback" element={<MicrosoftCallback />} />
              
              {/* Rutas protegidas */}
              <Route path="/app" element={
                <PrivateRoute>
                  <Layout />
                </PrivateRoute>
              }>
                <Route index element={<Dashboard />} />
                <Route path="reports" element={<Reports />} />
                <Route path="reports/:id" element={<ReportView />} />
                <Route path="history" element={<History />} />
                <Route path="storage" element={<Storage />} />
                <Route path="settings" element={<Settings />} />
                <Route path="profile" element={<Profile />} />
              </Route>

              {/* Ruta 404 */}
              <Route path="*" element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                    <p className="text-gray-600">Página no encontrada</p>
                    <a href="/" className="btn-primary mt-4 inline-block">
                      Volver al Inicio
                    </a>
                  </div>
                </div>
              } />
            </Routes>

            {/* Notificaciones toast */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  style: {
                    background: '#10B981',
                  },
                },
                error: {
                  duration: 5000,
                  style: {
                    background: '#EF4444',
                  },
                },
              }}
            />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;