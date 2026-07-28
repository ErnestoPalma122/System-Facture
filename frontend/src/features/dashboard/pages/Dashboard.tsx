import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { Sidebar } from '../components/Sidebar';
import { Header } from '../components/Header';

/**
 * Layout Principal del Sistema.
 * Envuelve todas las rutas protegidas con el Sidebar y el Header.
 */
export function Dashboard() {
  const { user } = useAuthStore();
  // Estado para controlar si el sidebar está abierto (expandido) o colapsado
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50 flex overflow-hidden">
      <Sidebar user={user} isOpen={isSidebarOpen} />
      
      <div className="flex-1 flex flex-col min-w-0 transition-all duration-300">
        <Header 
          user={user} 
          isSidebarOpen={isSidebarOpen} 
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} 
        />
        
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

/**
 * Página de inicio del Dashboard (se muestra cuando la ruta es exactamente "/")
 * Diseño mejorado con feedback visual profesional.
 */
export function DashboardHome() {
  const { user } = useAuthStore();

  const getSaludo = () => {
    const hora = new Date().getHours();
    if (hora < 12) return "Buenos días";
    if (hora < 18) return "Buenas tardes";
    return "Buenas noches";
  };

  const inicial = user?.nombre?.charAt(0).toUpperCase() || "U";

  return (
    <div className="space-y-8">
      {/* 1. SECCIÓN DE BIENVENIDA Y PERFIL */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl shadow-lg p-8 text-white flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-3xl font-bold border-2 border-white/30 shadow-inner">
            {inicial}
          </div>
          <div>
            <h2 className="text-3xl font-bold tracking-tight">
              {getSaludo()}, {user?.nombre?.split(' ')[0]} 👋
            </h2>
            <p className="text-blue-100 mt-1 text-lg">
              Bienvenido de nuevo al Sistema de Facturación Electrónica.
            </p>
            <div className="flex items-center gap-3 mt-3">
              <span className="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-sm font-medium border border-white/20">
                👤 {user?.rol.tipo.replace('_', ' ')}
              </span>
              <span className="text-blue-200 text-sm flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {user?.email}
              </span>
            </div>
          </div>
        </div>
        <div className="hidden md:block text-right">
          <p className="text-blue-200 text-sm font-medium uppercase tracking-wider">Fecha de hoy</p>
          <p className="text-2xl font-bold">
            {new Date().toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
      </div>

      {/* 2. TARJETAS DE ESTADÍSTICAS RÁPIDAS */}
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Resumen General
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
              </div>
              <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">+12% este mes</span>
            </div>
            <h4 className="text-gray-500 text-sm font-medium">Total Clientes</h4>
            <p className="text-3xl font-bold text-gray-900 mt-1">150</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-emerald-50 rounded-lg">
                <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
              </div>
              <span className="text-xs font-semibold text-gray-500 bg-gray-50 px-2 py-1 rounded-full">Actualizado hoy</span>
            </div>
            <h4 className="text-gray-500 text-sm font-medium">Productos en Catálogo</h4>
            <p className="text-3xl font-bold text-gray-900 mt-1">320</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-50 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              </div>
              <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">+8.5% vs mes anterior</span>
            </div>
            <h4 className="text-gray-500 text-sm font-medium">Ventas del Mes</h4>
            <p className="text-3xl font-bold text-gray-900 mt-1">$5,200.00</p>
          </div>
        </div>
      </div>

      {/* 3. SECCIÓN DE ACCESOS RÁPIDOS */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Accesos Rápidos</h3>
        <div className="flex flex-wrap gap-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Nuevo Cliente
          </button>
          <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            Generar DTE
          </button>
        </div>
      </div>
    </div>
  );
}