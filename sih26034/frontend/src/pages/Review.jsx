import React, { useState, useEffect } from 'react'
import { Check, X, Edit3, MessageSquare, AlertTriangle, ShieldCheck, CheckCircle2 } from 'lucide-react'

export default function Review({ inspectionId, onNavigateReport }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [editValues, setEditValues] = useState({})
  const [notes, setNotes] = useState({})

  const fetchInspection = async () => {
    if (!inspectionId) return
    setLoading(true)
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/inspections/${inspectionId}`)
      if (res.ok) {
        const json = await res.json()
        setData(json)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInspection()
  }, [inspectionId])

  const handleDecision = async (crId, decision) => {
    try {
      const formData = new FormData()
      formData.append('compliance_result_id', crId)
      formData.append('decision', decision)
      if (editValues[crId]) formData.append('edited_value', editValues[crId])
      if (notes[crId]) formData.append('note', notes[crId])
      formData.append('officer_id', 'OFFICER-MH-401')

      const res = await fetch(`http://127.0.0.1:8000/api/inspections/${inspectionId}/review`, {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        await fetchInspection()
      }
    } catch (e) {
      console.error(e)
      alert('Failed to record review decision.')
    }
  }

  if (!inspectionId) {
    return (
      <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl text-slate-400">
        No active inspection selected.
      </div>
    )
  }

  const results = data?.compliance_results || []
  const reviews = data?.review_decisions || []
  const reviewsByCr = {}
  reviews.forEach((r) => {
    reviewsByCr[r.compliance_result_id] = r
  })

  const uncertainResults = results.filter(
    (r) => r.review_status === 'UNCERTAIN' || r.status === 'CONFLICT' || r.status === 'UNCERTAIN'
  )

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Banner */}
      <div className="bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 border border-amber-900/40 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded-full border border-amber-500/20">
                Layer 9 • Human-in-the-Loop Officer Adjudication
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white">Officer Review Workspace</h2>
            <p className="text-sm text-slate-400 mt-1">
              The AI highlights uncertain facts, low-confidence OCR, and conflicting values. The authorized officer records the binding legal verdict.
            </p>
          </div>

          <button
            onClick={onNavigateReport}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-blue-600/20"
          >
            Generate Final Audit Report
          </button>
        </div>
      </div>

      {/* Review Cards */}
      {results.length === 0 ? (
        <div className="p-8 text-center text-slate-500">Run inspection analysis first.</div>
      ) : (
        <div className="space-y-4">
          {results.map((r) => {
            const rev = reviewsByCr[r.id]
            const isUncertain = r.review_status === 'UNCERTAIN' || r.status === 'CONFLICT' || r.status === 'UNCERTAIN'

            return (
              <div
                key={r.id}
                className={`p-5 rounded-2xl border transition ${
                  rev
                    ? 'bg-slate-900/40 border-slate-800'
                    : isUncertain
                    ? 'bg-amber-950/20 border-amber-500/40 shadow-lg shadow-amber-500/5'
                    : 'bg-slate-900/50 border-slate-800'
                }`}
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  {/* Left: Info */}
                  <div className="space-y-1.5 max-w-2xl">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                        {r.rule_id}
                      </span>
                      <h4 className="text-sm font-bold text-white">{r.requirement}</h4>
                      <span
                        className={`text-[10px] font-black font-mono uppercase px-2 py-0.5 rounded ${
                          r.status === 'PASS'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : r.status === 'FAIL'
                            ? 'bg-rose-500/10 text-rose-400'
                            : 'bg-amber-500/10 text-amber-400'
                        }`}
                      >
                        Engine Verdict: {r.status}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 font-mono">
                      Observed Fact: <span className="text-white font-bold">{r.observed_value}</span>
                    </p>
                    <p className="text-xs text-slate-400">{r.reason}</p>
                    <p className="text-[11px] text-slate-500 italic">{r.source_reference}</p>
                  </div>

                  {/* Right: Decision Controls */}
                  <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                    {rev ? (
                      <div className="p-3 bg-emerald-950/40 border border-emerald-500/30 rounded-xl text-right">
                        <div className="text-xs font-bold text-emerald-400 flex items-center justify-end gap-1">
                          <CheckCircle2 className="w-4 h-4" />
                          Adjudicated: {rev.decision}
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          Officer: {rev.officer_id}
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleDecision(r.id, 'CONFIRMED_PASS')}
                          className="flex items-center gap-1.5 px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs transition"
                        >
                          <Check className="w-3.5 h-3.5" />
                          Confirm PASS
                        </button>

                        <button
                          onClick={() => handleDecision(r.id, 'CONFIRMED_FAIL')}
                          className="flex items-center gap-1.5 px-3 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-lg text-xs transition"
                        >
                          <X className="w-3.5 h-3.5" />
                          Mark FAIL
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
