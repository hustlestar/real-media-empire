import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Copy, Check } from 'lucide-react'

interface TextViewerProps {
  text: string
  isMarkdown?: boolean
}

export default function TextViewer({ text, isMarkdown = false }: TextViewerProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative">
      <div className="absolute top-3 right-3 z-10">
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80 text-sm transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              Copy
            </>
          )}
        </button>
      </div>

      <div className="bg-card border border-border rounded-lg p-6 max-h-[600px] overflow-y-auto">
        {isMarkdown ? (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown>{text}</ReactMarkdown>
          </div>
        ) : (
          <pre className="whitespace-pre-wrap font-mono text-sm text-foreground leading-relaxed">
            {text}
          </pre>
        )}
      </div>
    </div>
  )
}