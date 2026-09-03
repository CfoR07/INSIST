import os

src_dir = r"n:\PROJECTS\INSIST\sih26034\frontend\src\pages"

# 1. Capture.jsx
with open(os.path.join(src_dir, "Capture.jsx"), "w", encoding="utf-8") as f:
    f.write("""import React, { useState } from 'react'
import { Upload, Camera, AlertCircle, CheckCircle2, RefreshCw, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react'

const VIEW_TYPES = [
  'Front View',
  'Back View',
  'MRP & Details Panel',
  'Side / Nutrition Panel',
  'Top / Bottom View',
  'Barcode / QR Code'
]

export default function Capture({ onInspectionCreated }) {
  const [productName, setProductName] = useState('Britannia Good Day Biscuits')
  const [brand, setBrand] = useState('Britannia')
  const [category, setCategory] = useState('Food')
  const [packageType, setPackageType] = useState('Pouch / Flow Wrap')
  const [officerId, setOfficerId] = useState('INSP-MH-401')
  const [location, setLocation] = useState('Mumbai Zonal Metrology Lab')

  const [createdId, setCreatedId] = useState(null)
  const [images, setImages] = useState([])
  const [isCreating, setIsCreating] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [selectedView, setSelectedView] = useState(VIEW_TYPES[0])

  const handleCreateInspection = async (e) => {
    e.preventDefault()
    setIsCreating(true)
    try {
      const formData = new FormData()
      formData.append('product_name', productName)
      formData.append('brand', brand)
      formData.append('category', category)
      formData.append('package_type', packageType)
      formData.append('officer_id', officerId)
      formData.append('location', location)

      const res = await fetch('http://127.0.0.1:8000/api/inspections', {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setCreatedId(data.inspection_id)
    } catch (err) {
      console.error(err)
      alert('Error connecting to backend server.')
    } finally {
      setIsCreating(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file || !createdId) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('view_type', selectedView)
      formData.append('file', file)

      const res = await fetch(`http://127.0.0.1:8000/api/inspections/${createdId}/upload`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setImages((prev) => [
        ...prev,
        {
          id: data.image_id,
          view_type: selectedView,
          url: `http://127.0.0.1:8000${data.image_url}`,
          quality: data.quality
        }
      ])
    } catch (err) {
      console.error(err)
      alert('Upload failed.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Info */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-900/60 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono font-semibold text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded-full border border-blue-500/20">
                Layer 1 & 2 • Capture & OpenCV Quality Gate
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white">Create Packaging Inspection</h2>
            <p className="text-sm text-slate-400 mt-1">
              Photographs undergo automated OpenCV blur (Laplacian variance), glare, and exposure checks prior to OCR extraction.
            </p>
          </div>
          {createdId && (
            <div className="bg-slate-950 border border-blue-500/40 px-4 py-2.5 rounded-xl text-right">
              <span className="text-xs text-slate-400 font-mono block">ACTIVE INSPECTION ID</span>
              <span className="text-xl font-mono font-bold text-blue-400">{createdId}</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Step 1: Inspection Metadata Form */}
        <div className="lg:col-span-5 bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2 pb-3 border-b border-slate-800">
            <span className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center text-xs font-bold font-mono">1</span>
            Inspection Metadata
          </h3>

          <form onSubmit={handleCreateInspection} className="space-y-3.5">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Product Description</label>
              <input
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                disabled={createdId}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-60"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Brand / Entity</label>
                <input
                  type="text"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  disabled={createdId}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-60"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Declared Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  disabled={createdId}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-60"
                >
                  <option value="Food">Food / Edible</option>
                  <option value="Cosmetics">Cosmetics / Personal Care</option>
                  <option value="Electronics">Electronics / Hardware</option>
                  <option value="General Commodity">General Commodity</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Officer Badge ID</label>
                <input
                  type="text"
                  value={officerId}
                  onChange={(e) => setOfficerId(e.target.value)}
                  disabled={createdId}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-60 font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Zonal Lab / Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  disabled={createdId}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-60"
                />
              </div>
            </div>

            {!createdId ? (
              <button
                type="submit"
                disabled={isCreating}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 rounded-xl text-sm transition shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2"
              >
                {isCreating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                Initialize Inspection Session
              </button>
            ) : (
              <div className="p-3 bg-emerald-950/40 border border-emerald-500/30 rounded-xl flex items-center gap-2 text-xs text-emerald-400 font-semibold">
                <CheckCircle2 className="w-4 h-4" />
                Session Initialized ({createdId})
              </div>
            )}
          </form>
        </div>

        {/* Step 2: Upload Views & OpenCV Quality Results */}
        <div className="lg:col-span-7 bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-5">
          <h3 className="text-base font-bold text-white flex items-center justify-between pb-3 border-b border-slate-800">
            <span className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center text-xs font-bold font-mono">2</span>
              Package Photographs & OpenCV Quality Gate
            </span>
            <span className="text-xs font-mono text-slate-400">{images.length} Captured</span>
          </h3>

          {!createdId ? (
            <div className="p-10 text-center border-2 border-dashed border-slate-800 rounded-2xl text-slate-500 space-y-2">
              <Camera className="w-10 h-10 mx-auto opacity-40" />
              <p className="text-sm font-medium">Please initialize an inspection session on the left first.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* View Selector & Upload Button */}
              <div className="flex flex-wrap gap-2 items-center">
                <select
                  value={selectedView}
                  onChange={(e) => setSelectedView(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  {VIEW_TYPES.map((v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>

                <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold cursor-pointer transition shadow-sm">
                  <Upload className="w-4 h-4" />
                  {isUploading ? 'Evaluating OpenCV Quality...' : `Upload ${selectedView}`}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    disabled={isUploading}
                    className="hidden"
                  />
                </label>
              </div>

              {/* Uploaded Images List with Quality Metrics */}
              <div className="space-y-3">
                {images.length === 0 ? (
                  <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
                    No packaging photographs uploaded yet. Upload Front view and MRP/Details panel to proceed.
                  </div>
                ) : (
                  images.map((img, idx) => (
                    <div
                      key={img.id}
                      className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between gap-4"
                    >
                      <div className="flex items-center gap-3">
                        <img
                          src={img.url}
                          alt={img.view_type}
                          className="w-14 h-14 object-cover rounded-lg border border-slate-800 bg-slate-900"
                        />
                        <div>
                          <span className="text-xs font-bold text-white block">{img.view_type}</span>
                          <span className="text-[10px] font-mono text-slate-400">{img.id}</span>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-[10px] text-slate-400 font-mono">
                              Laplacian Var: {img.quality.blur_metric}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              Brightness: {img.quality.brightness_metric}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <span
                          className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider font-mono ${
                            img.quality.quality_status === 'SHARP'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : img.quality.quality_status === 'USABLE'
                              ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/30 animate-pulse'
                          }`}
                        >
                          {img.quality.quality_status} ({Math.round(img.quality.quality_score * 100)}%)
                        </span>

                        {!img.quality.usable && (
                          <span className="block text-[10px] text-rose-400 font-semibold mt-1 flex items-center justify-end gap-1">
                            <AlertCircle className="w-3 h-3" /> Retake Recommended
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Proceed to Inspection */}
              {images.length > 0 && (
                <div className="pt-3 border-t border-slate-800 flex justify-end">
                  <button
                    onClick={() => onInspectionCreated(createdId)}
                    className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl text-xs shadow-lg shadow-blue-600/30 transition"
                  >
                    Proceed to OCR & Deterministic Compliance Engine
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
""")

print("Capture.jsx created")
