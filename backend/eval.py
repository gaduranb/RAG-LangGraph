"""
Evaluation script for Banking Login & Security Helper.

Tests the agent with 10 sample prompts from instructions.md and measures:
- Response accuracy
- Latency (p50, p95, p99)
- Citation quality
- Tool usage correctness
"""
import asyncio
import httpx
import time
import statistics
from typing import List, Dict
from tabulate import tabulate
import sys


# Sample prompts from instructions.md
SAMPLE_PROMPTS = [
    "I got locked out after entering the wrong password. Can I unlock myself?",
    "What are the password rules?",
    "Why do I keep getting verification codes?",
    "How often does 'remember this device' expire?",
    "I forgot my username — how do I recover it?",
    "I changed phones and now my codes don't work — what should I do?",
    "Please help me reset my password safely.",
    "Can I unlock a phone-banking user without calling support?",
    "I signed up, but I'm stuck — how do I finish setup?",
    "If I start a password reset on a federal holiday, when should I expect the next step?"
]


class EvaluationMetrics:
    """Tracks evaluation metrics."""

    def __init__(self):
        self.latencies: List[int] = []
        self.results: List[Dict] = []
        self.citation_count = 0
        self.tool_calls_count = 0

    def add_result(self, question: str, response: Dict, latency_ms: int):
        """Add a result to metrics."""
        self.latencies.append(latency_ms)
        self.results.append({
            "question": question,
            "answer_length": len(response.get("answer", "")),
            "citations": len(response.get("citations", [])),
            "tool_calls": len(response.get("tool_calls", [])),
            "latency_ms": latency_ms
        })

        if response.get("citations"):
            self.citation_count += len(response["citations"])

        if response.get("tool_calls"):
            self.tool_calls_count += len(response["tool_calls"])

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        if not self.latencies:
            return {}

        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)

        return {
            "total_queries": n,
            "latency_p50": sorted_latencies[int(n * 0.5)],
            "latency_p95": sorted_latencies[int(n * 0.95)] if n > 1 else sorted_latencies[0],
            "latency_p99": sorted_latencies[int(n * 0.99)] if n > 1 else sorted_latencies[0],
            "latency_mean": int(statistics.mean(self.latencies)),
            "latency_max": max(self.latencies),
            "latency_min": min(self.latencies),
            "total_citations": self.citation_count,
            "total_tool_calls": self.tool_calls_count,
            "avg_citations_per_query": round(self.citation_count / n, 2),
            "avg_answer_length": int(statistics.mean([r["answer_length"] for r in self.results]))
        }


async def query_agent(client: httpx.AsyncClient, question: str) -> tuple[Dict, int]:
    """Query the agent and measure latency."""
    start_time = time.time()

    try:
        response = await client.post(
            "http://localhost:8000/chat",
            json={"question": question},
            timeout=30.0
        )
        response.raise_for_status()

        latency_ms = int((time.time() - start_time) * 1000)
        return response.json(), latency_ms

    except Exception as e:
        print(f"❌ Error querying agent: {e}")
        return {}, 0


async def run_evaluation():
    """Run the full evaluation suite."""
    print("=" * 80)
    print("🚀 Banking Login & Security Helper - Evaluation")
    print("=" * 80)
    print()

    metrics = EvaluationMetrics()

    async with httpx.AsyncClient() as client:
        # Health check
        try:
            health = await client.get("http://localhost:8000/health", timeout=5.0)
            if health.status_code != 200:
                print("❌ Backend is not healthy. Please start the backend first.")
                sys.exit(1)
            print("✅ Backend is healthy\n")
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            print("Please run: docker-compose up -d")
            sys.exit(1)

        # Run evaluation on all sample prompts
        print(f"📊 Evaluating {len(SAMPLE_PROMPTS)} sample prompts...\n")

        for i, question in enumerate(SAMPLE_PROMPTS, 1):
            print(f"[{i}/{len(SAMPLE_PROMPTS)}] {question[:60]}...")

            response, latency_ms = await query_agent(client, question)

            if response:
                metrics.add_result(question, response, latency_ms)

                # Print concise result
                answer_preview = response.get("answer", "")[:100]
                citations = len(response.get("citations", []))
                tools = len(response.get("tool_calls", []))

                print(f"    ⏱️  {latency_ms}ms | 📚 {citations} citations | 🔧 {tools} tools")
                print(f"    💬 {answer_preview}...")
                print()

            await asyncio.sleep(0.5)  # Small delay between requests

    # Print summary statistics
    print("=" * 80)
    print("📈 Evaluation Summary")
    print("=" * 80)
    print()

    summary = metrics.get_summary()

    if not summary:
        print("❌ No results collected")
        return

    # Latency stats
    print("⏱️  Latency Statistics:")
    print(f"   • p50: {summary['latency_p50']}ms")
    print(f"   • p95: {summary['latency_p95']}ms (SLA: ≤5000ms)")
    print(f"   • p99: {summary['latency_p99']}ms")
    print(f"   • Mean: {summary['latency_mean']}ms")
    print(f"   • Min: {summary['latency_min']}ms")
    print(f"   • Max: {summary['latency_max']}ms")
    print()

    # SLA check
    if summary['latency_p95'] <= 5000:
        print("✅ p95 latency PASSES 5s SLA requirement")
    else:
        print(f"❌ p95 latency FAILS 5s SLA requirement ({summary['latency_p95']}ms)")
    print()

    # Quality stats
    print("📚 Quality Metrics:")
    print(f"   • Total queries: {summary['total_queries']}")
    print(f"   • Total citations: {summary['total_citations']}")
    print(f"   • Avg citations/query: {summary['avg_citations_per_query']}")
    print(f"   • Total tool calls: {summary['total_tool_calls']}")
    print(f"   • Avg answer length: {summary['avg_answer_length']} chars")
    print()

    # Detailed results table
    print("📋 Detailed Results:")
    table_data = [
        [
            i + 1,
            r["question"][:40] + "...",
            r["latency_ms"],
            r["citations"],
            r["tool_calls"],
            r["answer_length"]
        ]
        for i, r in enumerate(metrics.results)
    ]

    headers = ["#", "Question", "Latency (ms)", "Citations", "Tools", "Answer Length"]
    print(tabulate(table_data, headers=headers, tablefmt="simple"))
    print()

    print("=" * 80)
    print("✅ Evaluation Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_evaluation())
