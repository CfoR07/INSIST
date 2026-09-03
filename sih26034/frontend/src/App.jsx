import React, { useState, useEffect } from 'react'
import { Camera, ShieldCheck, FileSearch, ClipboardCheck, LayoutDashboard, FileText, AlertTriangle, Layers } from 'lucide-react'
import Capture from './pages/Capture'
import Inspection from './pages/Inspection'
import Review from './pages/Review'
import Report from './pages/Report'
import Dashboard from './pages/Dashboard'

export default function App() {
  const [activeTab, setActiveTab] = useState('capture')
  const [currentInspectionId, setCurrentInspectionId] = useState(null)
  const [stats, setStats] = useState(null)

  const fetchStats = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/dashboard/stats')
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-xl shadow-lg shadow-blue-500/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-black tracking-tight text-lg text-white">SIH26034</span>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
                  LMPC Metrology AI
                </span>
              </div>
              <p className="text-xs text-slate-400">AI-Assisted Pre-Packed Commodity Inspection</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/80">
            <button
              onClick={() => setActiveTab('capture')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'capture'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Camera className="w-4 h-4" />
              1. Capture & Quality
            </button>

            <button
              onClick={() => setActiveTab('inspection')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'inspection'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <FileSearch className="w-4 h-4" />
              2. Inspect & Evidence
              {currentInspectionId && (
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('review')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'review'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <ClipboardCheck className="w-4 h-4" />
              3. Officer Review
              {stats?.pending_reviews > 0 && (
                <span className="px-1.5 py-0.2 bg-amber-500 text-slate-950 font-bold rounded-full text-[10px]">
                  {stats.pending_reviews}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('report')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'report'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <FileText className="w-4 h-4" />
              4. Audit Report
            </button>

            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'dashboard'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </button>
          </nav>

          {/* Philosophy Motto */}
          <div className="hidden lg:flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>AI reads. Code decides.</span>
          </div>
        </div>
      </header>

      {/* Main Content View */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'capture' && (
          <Capture
            onInspectionCreated={(id) => {
              setCurrentInspectionId(id)
              setActiveTab('inspection')
              fetchStats()
            }}
          />
        )}

        {activeTab === 'inspection' && (
          <Inspection
            inspectionId={currentInspectionId}
            onNavigateReview={() => setActiveTab('review')}
            onNavigateReport={() => setActiveTab('report')}
          />
        )}

        {activeTab === 'review' && (
          <Review
            inspectionId={currentInspectionId}
            onNavigateReport={() => setActiveTab('report')}
          />
        )}

        {activeTab === 'report' && (
          <Report inspectionId={currentInspectionId} />
        )}

        {activeTab === 'dashboard' && (
          <Dashboard
            stats={stats}
            onSelectInspection={(id) => {
              setCurrentInspectionId(id)
              setActiveTab('inspection')
            }}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500 font-mono">
        SIH26034 Prototype • Legal Metrology (Packaged Commodities) Rules 2011 Automated Audit Platform
      </footer>
    </div>
  )
}
