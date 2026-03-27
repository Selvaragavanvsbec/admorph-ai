import React from 'react'

export default function VariantExplorerPage({ variants, onSelect }) {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Variant Explorer</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {variants.map((variant, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow p-3 space-y-2">
            <img src={variant.image_url} alt={variant.headline} className="rounded-lg w-full h-52 object-cover bg-slate-100" />
            <div className="font-semibold">{variant.headline}</div>
            <div className="text-sm">CTA: {variant.cta}</div>
            <div className="text-sm">Score: {variant.score}</div>
            <button className="primary" onClick={() => onSelect(variant)}>Edit</button>
          </div>
        ))}
      </div>
    </div>
  )
}
