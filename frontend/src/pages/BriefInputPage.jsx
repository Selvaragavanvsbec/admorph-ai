import React from 'react'

export default function BriefInputPage({ form, setForm, onGenerate, loading }) {
  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Brief Input</h2>
      <div className="grid md:grid-cols-2 gap-4">
        <input value={form.product} onChange={(e) => update('product', e.target.value)} placeholder="Product" />
        <input value={form.audience} onChange={(e) => update('audience', e.target.value)} placeholder="Audience" />
        <input value={form.goal} onChange={(e) => update('goal', e.target.value)} placeholder="Goal" />
        <select value={form.platform} onChange={(e) => update('platform', e.target.value)}>
          <option>instagram</option>
          <option>facebook</option>
          <option>linkedin</option>
          <option>youtube</option>
        </select>
        <input value={form.tone} onChange={(e) => update('tone', e.target.value)} placeholder="Brand tone" />
        <input value={form.brand_colors} onChange={(e) => update('brand_colors', e.target.value)} placeholder="#0F172A,#F8FAFC" />
      </div>
      <textarea value={form.description} onChange={(e) => update('description', e.target.value)} placeholder="Description" rows={4} />
      <button className="primary" onClick={onGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Ads'}
      </button>
    </div>
  )
}
