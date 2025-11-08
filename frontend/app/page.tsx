"use client"

import { useState, useRef, useEffect } from "react"
import ChatMessage from "@/components/chat-message"
import ChatInput from "@/components/chat-input"
import ExamplePrompts from "@/components/example-prompts"

interface Message {
  id: string
  type: "user" | "assistant"
  text: string
  citations?: Array<{ title: string; url: string }>
  timing_ms?: number
}

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (question: string) => {
    if (!question.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      text: question,
    }

    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
      const response = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        text: data.answer,
        citations: data.citations || [],
        timing_ms: data.timing_ms,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        text: "Sorry, I encountered an error. Please try again.",
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background to-accent/5 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl flex flex-col h-screen md:h-[600px] bg-card rounded-2xl shadow-xl border border-border overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground px-6 py-4 sm:px-8 sm:py-6">
          <h1 className="text-xl sm:text-2xl font-semibold text-balance">🏦 Banking Login & Security Helper</h1>
          <p className="text-primary-foreground/80 text-xs sm:text-sm mt-1">
            Get instant answers to your banking questions
          </p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.length === 0 ? (
            <ExamplePrompts onSelect={handleSendMessage} />
          ) : (
            messages.map((message) => <ChatMessage key={message.id} message={message} />)
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-border p-4 sm:p-6 bg-card">
          <ChatInput onSend={handleSendMessage} disabled={loading} />
        </div>
      </div>
    </main>
  )
}
