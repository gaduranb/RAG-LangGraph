"use client"

import { useState } from "react"
import { ChevronDown, ExternalLink } from "lucide-react"

interface ChatMessageProps {
  message: {
    type: "user" | "assistant"
    text: string
    citations?: Array<{ title: string; url: string }>
    timing_ms?: number
  }
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [showCitations, setShowCitations] = useState(false)

  if (message.type === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-xs sm:max-w-sm bg-primary text-primary-foreground rounded-2xl rounded-tr-none px-4 py-3">
          <p className="text-sm sm:text-base leading-relaxed">{message.text}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-xs sm:max-w-sm space-y-3">
        <div className="bg-muted/50 text-foreground rounded-2xl rounded-tl-none px-4 py-3">
          <p className="text-sm sm:text-base leading-relaxed text-pretty">{message.text}</p>
        </div>

        {/* Footer with timing and citations toggle */}
        <div className="flex items-center justify-between px-2 text-xs text-muted-foreground">
          {message.timing_ms && (
            <span className="bg-accent/20 text-accent-foreground px-2 py-1 rounded-full text-xs font-medium">
              ⚡ {message.timing_ms}ms
            </span>
          )}
          {message.citations && message.citations.length > 0 && (
            <button
              onClick={() => setShowCitations(!showCitations)}
              className="flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors ml-auto"
              aria-expanded={showCitations}
            >
              <span className="text-xs font-medium">
                {message.citations.length} {message.citations.length === 1 ? "source" : "sources"}
              </span>
              <ChevronDown
                size={14}
                className={`transition-transform duration-200 ${showCitations ? "rotate-180" : ""}`}
              />
            </button>
          )}
        </div>

        {/* Citations Section */}
        {showCitations && message.citations && message.citations.length > 0 && (
          <div className="bg-muted/30 border border-border rounded-lg p-3 space-y-2">
            <p className="text-xs font-semibold text-foreground">Sources</p>
            {message.citations.map((citation, idx) => (
              <a
                key={idx}
                href={citation.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 text-xs text-primary hover:text-primary/80 transition-colors group"
              >
                <ExternalLink size={12} className="mt-0.5 flex-shrink-0" />
                <span className="underline group-hover:no-underline">{citation.title}</span>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
