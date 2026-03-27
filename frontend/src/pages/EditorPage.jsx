import React, { useState } from 'react'

export default function EditorPage({ variant, onEdit }) {
  const [command, setCommand] = useState('')

  if (!variant) {
    return <div className="text-sm">Select a variant from explorer to start editing.</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Conversational Editor</h2>
      <div className="bg-white rounded-xl p-4 shadow space-y-2">
        <img src={variant.image_url} alt={variant.headline} className="rounded-lg w-full max-w-md" />
        <div><strong>Headline:</strong> {variant.headline}</div>
        <div><strong>CTA:</strong> {variant.cta}</div>
        <div><strong>Theme:</strong> {variant.visual_theme}</div>
      </div>

      <input
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        placeholder='Example: "make headline more urgent"'
      />
      <button
        className="primary"
        onClick={() => {
          onEdit(command)
          setCommand('')
        }}
      >
        Apply Edit
      </button>
    </div>
  )
}
