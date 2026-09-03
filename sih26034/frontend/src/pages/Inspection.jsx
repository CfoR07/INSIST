import React, { useState, useEffect } from 'react'
import { Play, CheckCircle2, XCircle, AlertTriangle, HelpCircle, Layers, ArrowRight, Eye, RefreshCw, Bookmark, Cpu } from 'lucide-react'

export default function Inspection({ inspectionId, onNavigateReview, onNavigateReport }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [selectedFactId, setSelectedFactId] = useState(null)
  const [activeImageIndex, setActiveImageIndex] = useState(0)

  const fetchInspectionData = async () => {
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
    fetchInspectionData()
  }, [inspectionId])

  const runAnalysisPipeline = async () => {
    if (!inspectionId) return
    setAnalyzing(true)
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/inspections/${inspectionId}/analyze`, {
        method: 'POST'
      })
      if (res.ok) {
        await fetchInspectionData()
      }
    } catch (e) {
      console.error(e)
      alert('Analysis execution failed.')
    } finally {
      setAnalyzing(false)
    }
  }

  if (!inspectionId) {
    return (
      <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl">
        <Cpu className="w-12 h-12 text-blue-500/40 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-white">No Active Inspection Selected</h3>
        <p className="text-sm text-slate-400 mt-1">Please create or select an inspection session to view findings.</p>
      </div>
    )
  }

  const images = data?.images || []
  const facts = data?.facts || []
  const results = data?.compliance_results || []
  const activeImage = images[activeImageIndex]

  // Find fact coordinates to highlight
  const selectedFact = facts.find((f) => f.id === selectedFactId)

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono uppercase bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20 font-bold">
              Layer 3-8 • OCR Extraction & Deterministic Engine
            </span>
            <span className="text-xs font-mono text-slate-400">ID: {inspectionId}</span>
          </div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            {data?.inspection?.product_name || 'Inspection Workspace'}
            <span className="text-xs font-normal text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
              Category: {data?.inspection?.category}
            </span>
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={runAnalysisPipeline}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-blue-600/20 disabled:opacity-50"
          >
            {analyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {results.length > 0 ? 'Re-Run Compliance Engine' : 'Run Deterministic Engine'}
          </button>

          {results.some((r) => r.review_status === 'UNCERTAIN') ? (
            <button
              onClick={onNavigateReview}
              className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs transition shadow-lg shadow-amber-500/20 animate-pulse"
            >
              <AlertTriangle className="w-4 h-4" />
              Officer Review Required
            </button>
          ) : results.length > 0 ? (
            <button
              onClick={onNavigateReport}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-emerald-600/20"
            >
              <CheckCircle2 className="w-4 h-4" />
              View Final Report
            </button>
          ) : null}
        </div>
      </div>

      {/* Dual Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Pane: Interactive Image Canvas with Bounding Boxes */}
        <div className="lg:col-span-6 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Eye className="w-4 h-4 text-blue-400" />
              Packaging Evidence Viewer
            </h3>
            {/* Image View Selector */}
            <div className="flex gap-1">
              {images.map((img, idx) => (
                <button
                  key={img.id}
                  onClick={() => {
                    setActiveImageIndex(idx)
                    setSelectedFactId(null)
                  }}
                  className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition ${
                    activeImageIndex === idx
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {img.view_type}
                </button>
              ))}
            </div>
          </div>

          {/* Canvas Box */}
          <div className="relative aspect-square w-full bg-slate-950 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center">
            {activeImage ? (
              <div className="relative w-full h-full">
                <img
                  src={`http://127.0.0.1:8000${activeImage.image_url}`}
                  alt={activeImage.view_type}
                  className="w-full h-full object-contain select-none"
                />

                {/* Render Bounding Boxes for this image */}
                {facts
                  .filter((f) => f.source_image_id === activeImage.id && f.bounding_box && f.bounding_box.length === 4)
                  .map((f) => {
                    const [ymin, xmin, ymax, xmax] = f.bounding_box
                    const top = `${(ymin / 1000) * 100}%`
                    const left = `${(xmin / 1000) * 100}%`
                    const width = `${((xmax - xmin) / 1000) * 100}%`
                    const height = `${((ymax - ymin) / 1000) * 100}%`

                    const isSelected = selectedFactId === f.id

                    return (
                      <div
                        key={f.id}
                        onClick={() => setSelectedFactId(f.id)}
                        style={{ top, left, width, height }}
                        className={`absolute cursor-pointer transition-all duration-150 rounded ${
                          isSelected
                            ? 'border-2 border-emerald-400 bg-emerald-500/30 shadow-[0_0_15px_rgba(52,211,153,0.8)] z-30'
                            : 'border border-blue-400/80 bg-blue-500/15 hover:bg-blue-500/30 z-10'
                        }`}
                      >
                        <span
                          className={`absolute -top-5 left-0 px-1.5 py-0.2 text-[9px] font-mono font-bold rounded shadow ${
                            isSelected ? 'bg-emerald-500 text-slate-950' : 'bg-blue-600 text-white'
                          }`}
                        >
                          {f.field_name} ({Math.round(f.confidence * 100)}%)
                        </span>
                      </div>
                    )
                  })}
              </div>
            ) : (
              <span className="text-xs text-slate-500">No image loaded</span>
            )}
          </div>

          {/* Selected Fact Provenance Card */}
          {selectedFact ? (
            <div className="p-3 bg-slate-950 border border-emerald-500/40 rounded-xl space-y-1 animate-fadeIn">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-emerald-400 font-bold uppercase">{selectedFact.field_name}</span>
                <span className="text-slate-400">Confidence: {Math.round(selectedFact.confidence * 100)}%</span>
              </div>
              <div className="text-sm font-bold text-white">{selectedFact.value}</div>
              <div className="text-[10px] text-slate-400 font-mono">
                Source: {selectedFact.source_image_id} • Status: {selectedFact.extraction_status}
              </div>
            </div>
          ) : (
            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-center text-xs text-slate-500">
              Click any bounding box or rule on the right to trace visual evidence.
            </div>
          )}
        </div>

        {/* Right Pane: Extracted Facts & Deterministic Compliance Engine */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-400" />
                Deterministic Statutory Rule Verdicts
              </span>
              <span className="text-xs font-mono text-slate-400">{results.length} LMPC Rules Evaluated</span>
            </h3>

            {results.length === 0 ? (
              <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs space-y-2">
                <Cpu className="w-8 h-8 mx-auto opacity-30" />
                <p>Click "Run Deterministic Engine" above to evaluate legal compliance.</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[560px] overflow-y-auto pr-1">
                {results.map((r) => {
                  const fact = facts.find((f) => r.evidence_fact_ids?.includes(f.id))

                  return (
                    <div
                      key={r.id}
                      onClick={() => {
                        if (fact) {
                          setSelectedFactId(fact.id)
                          const imgIdx = images.findIndex((img) => img.id === fact.source_image_id)
                          if (imgIdx !== -1) setActiveImageIndex(imgIdx)
                        }
                      }}
                      className={`p-3.5 rounded-xl border transition cursor-pointer ${
                        r.status === 'PASS'
                          ? 'bg-emerald-950/20 border-emerald-900/50 hover:border-emerald-500/50'
                          : r.status === 'FAIL'
                          ? 'bg-rose-950/20 border-rose-900/50 hover:border-rose-500/50'
                          : r.status === 'CONFLICT'
                          ? 'bg-purple-950/20 border-purple-900/50 hover:border-purple-500/50'
                          : r.status === 'UNCERTAIN'
                          ? 'bg-amber-950/20 border-amber-900/50 hover:border-amber-500/50'
                          : 'bg-slate-950 border-slate-800'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono font-bold text-slate-400">{r.rule_id}</span>
                            <span className="text-xs font-bold text-white">{r.requirement}</span>
                          </div>
                          <p className="text-[11px] text-slate-400 mt-1 font-mono">
                            Observed: <span className="text-slate-200 font-semibold">{r.observed_value || '—'}</span>
                          </p>
                          <p className="text-[11px] text-slate-400 mt-0.5">{r.reason}</p>
                        </div>

                        {/* Status Badge */}
                        <div className="text-right">
                          <span
                            className={`px-2.5 py-1 rounded text-[10px] font-black font-mono uppercase tracking-wider inline-block ${
                              r.status === 'PASS'
                                ? 'bg-emerald-500 text-slate-950'
                                : r.status === 'FAIL'
                                ? 'bg-rose-600 text-white'
                                : r.status === 'CONFLICT'
                                ? 'bg-purple-600 text-white animate-pulse'
                                : r.status === 'UNCERTAIN'
                                ? 'bg-amber-500 text-slate-950'
                                : 'bg-slate-800 text-slate-300'
                            }`}
                          >
                            {r.status}
                          </span>

                          {r.review_status === 'UNCERTAIN' && (
                            <span className="block text-[9px] font-bold text-amber-400 font-mono mt-1">
                              [NEEDS REVIEW]
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
