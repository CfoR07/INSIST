import React, { useState, useEffect } from 'react'
import { ShieldCheck, CheckCircle, XCircle, AlertTriangle, Clock, ArrowUpRight, BarChart3 } from 'lucide-react'

export default function Dashboard({ stats, onSelectInspection }) {
  const [inspections, setInspections] = useState([])

  useEffect(() => {
    const fetchInspections = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/inspections')
        if (res.ok) {
          const list = await res.json()
          setInspections(list)
        }
      } catch (e) {
        console.error(e)
      }
    }
    fetchInspections()
  }, [])

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-900/60 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-2xl font-bold text-white">Metrology Enforcement Intelligence Dashboard</h2>
        <p className="text-sm text-slate-400 mt-1">
          Real-time analytics on pre-packed commodity inspections, compliance rates, common statutory violations, and review queues.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-mono text-slate-400 uppercase font-bold">Total Inspections</div>
          <div className="text-3xl font-black text-white mt-1">{stats?.total_inspections || 0}</div>
          <div className="text-[11px] text-blue-400 font-semibold mt-2 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> All Sessions Recorded
          </div>
        </div>

        <div className="bg-emerald-950/20 border border-emerald-900/40 p-5 rounded-2xl">
          <div className="text-xs font-mono text-emerald-400 uppercase font-bold">Rule Checks Passed</div>
          <div className="text-3xl font-black text-emerald-400 mt-1">{stats?.pass_count || 0}</div>
          <div className="text-[11px] text-emerald-500 font-semibold mt-2 flex items-center gap-1">
            <CheckCircle className="w-3.5 h-3.5" /> Statutory Satisfied
          </div>
        </div>

        <div className="bg-rose-950/20 border border-rose-900/40 p-5 rounded-2xl">
          <div className="text-xs font-mono text-rose-400 uppercase font-bold">Violations Detected</div>
          <div className="text-3xl font-black text-rose-400 mt-1">{stats?.fail_count || 0}</div>
          <div className="text-[11px] text-rose-400 font-semibold mt-2 flex items-center gap-1">
            <XCircle className="w-3.5 h-3.5" /> LMPC Non-Compliant
          </div>
        </div>

        <div className="bg-amber-950/20 border border-amber-900/40 p-5 rounded-2xl">
          <div className="text-xs font-mono text-amber-400 uppercase font-bold">Pending Officer Reviews</div>
          <div className="text-3xl font-black text-amber-400 mt-1">{stats?.pending_reviews || 0}</div>
          <div className="text-[11px] text-amber-400 font-semibold mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Awaiting Adjudication
          </div>
        </div>
      </div>

      {/* Common Violations & Recent Inspections */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Top Violations */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2 pb-3 border-b border-slate-800">
            <BarChart3 className="w-4 h-4 text-rose-400" />
            Most Frequent LMPC Rule Violations
          </h3>

          <div className="space-y-3">
            {stats?.common_violations && stats.common_violations.length > 0 ? (
              stats.common_violations.map((v) => (
                <div key={v.rule_id} className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-rose-400">{v.rule_id}</span>
                    <span className="text-slate-400 font-bold">{v.count} Violations</span>
                  </div>
                  <div className="text-xs font-semibold text-white mt-1">{v.requirement}</div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-500">No violations logged yet.</div>
            )}
          </div>
        </div>

        {/* Right: Inspection History Table */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2 pb-3 border-b border-slate-800">
            <Clock className="w-4 h-4 text-blue-400" />
            Recent Inspections Log (Layer 12 History)
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono">
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">Product Name</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 px-3 font-mono text-blue-400 font-bold">{insp.id}</td>
                    <td className="py-2.5 px-3 text-white font-medium">{insp.product_name}</td>
                    <td className="py-2.5 px-3 text-slate-300">{insp.category}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300">
                        {insp.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <button
                        onClick={() => onSelectInspection(insp.id)}
                        className="flex items-center gap-1 text-blue-400 hover:text-blue-300 font-bold"
                      >
                        Open <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
