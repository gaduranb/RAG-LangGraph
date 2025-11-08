"use client"

interface ExamplePromptsProps {
  onSelect: (prompt: string) => void
}

const EXAMPLE_PROMPTS = [
  "🔑 I forgot my password",
  "✉️ Why do I get verification codes?",
  "🔐 How do I enable two-factor authentication?",
  "🛡️ Is my account secure?",
]

export default function ExamplePrompts({ onSelect }: ExamplePromptsProps) {
  return (
    <div className="h-full flex flex-col items-center justify-center space-y-8">
      <div className="text-center space-y-2">
        <p className="text-sm text-muted-foreground">How can we help you today?</p>
        <p className="text-xs text-muted-foreground/60">Try one of these common questions</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-sm">
        {EXAMPLE_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(prompt)}
            className="bg-muted hover:bg-muted/80 text-foreground text-left text-sm p-4 rounded-lg border border-border transition-all hover:border-primary/50 hover:shadow-sm"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  )
}
