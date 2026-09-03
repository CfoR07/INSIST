import React, { useState, useEffect } from 'react'
import { Download, Printer, ShieldCheck, FileText, CheckCircle2 } from 'lucide-react'

export default function Report({ inspectionId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

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

  if (!inspectionId) {
    return (
      <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl text-slate-400">
        No active inspection selected.
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Action Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono font-bold text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded-full border border-blue-500/20">
              Layer 11 • Auditable Statutory Legal Metrology Report
            </span>
          </div>
          <h2 className="text-xl font-bold text-white">Inspection Audit Certificate #{inspectionId}</h2>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={`http://127.0.0.1:8000/api/inspections/${inspectionId}/report/pdf`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-blue-600/20"
          >
            <Download className="w-4 h-4" />
            Download PDF Report
          </a>

          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl text-xs transition"
          >
            <Printer className="w-4 h-4" />
            Print Certificate
          </button>
        </div>
      </div>

      {/* Embedded HTML Report Frame */}
      <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border border-slate-800 min-h-[700px]">
        <iframe
          src={`http://127.0.0.1:8000/api/inspections/${inspectionId}/report`}
          title="Official Inspection Report"
          className="w-full min-h-[750px] border-none"
        />
      </div>
    </div>
  )
}
