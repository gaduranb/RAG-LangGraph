"use client"

import type React from "react"

import { useState } from "react"
import { Send } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      onSend(input)
      setInput("")
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        placeholder="Ask about passwords, verification codes, security..."
        className="flex-1 bg-input text-foreground placeholder:text-muted-foreground rounded-full px-4 py-3 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all disabled:opacity-50"
        aria-label="Chat message input"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed rounded-full p-3 transition-colors flex-shrink-0"
        aria-label="Send message"
      >
        <Send size={20} />
      </button>
    </form>
  )
}
