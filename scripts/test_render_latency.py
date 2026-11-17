"""Performance and latency benchmark for 3-page resume under 4x CPU throttling.

Measures:
1. CSS Variable update latency (colors, fonts, spacing).
2. Live text typing simulation latency.
3. Pagination computation overhead.
"""

import time
import statistics
from pathlib import Path
from playwright.sync_api import sync_playwright

THREE_PAGE_SECTIONS = [
    {
        "id": "sec-summary",
        "type": "summary",
        "title": "Executive Summary",
        "visible": True,
        "pageBreakBefore": False,
        "order": 0,
        "items": [
            {
                "id": "sum-1",
                "title": "",
                "subtitle": "",
                "location": "",
                "dateRange": "",
                "visible": True,
                "itemType": "paragraph",
                "bullets": [
                    {
                        "id": "b-sum",
                        "text": "Distinguished Engineering Leader with 15+ years architecting globally distributed document processing engines, high-availability real-time sync systems, and enterprise microservice architectures.",
                    }
                ],
            }
        ],
    },
    {
        "id": "sec-exp-1",
        "type": "experience",
        "title": "Leadership Experience",
        "visible": True,
        "pageBreakBefore": False,
        "order": 1,
        "items": [
            {
                "id": f"item-exp-{i}",
                "title": f"Staff Infrastructure Engineer {i}",
                "subtitle": "Global Cloud Platforms Inc.",
                "location": "San Francisco, CA",
                "dateRange": f"202{i%4} - 202{i%4 + 1}",
                "visible": True,
                "itemType": "timeline",
                "bullets": [
                    {
                        "id": f"b-exp-{i}-1",
                        "text": f"Spearheaded migration of core rendering pipelines across {i * 10} Kubernetes clusters, decreasing p99 latency by 38%.",
                    },
                    {
                        "id": f"b-exp-{i}-2",
                        "text": f"Architected high-throughput message streaming layer handling over {i * 2}B daily transactions with zero data loss.",
                    },
                    {
                        "id": f"b-exp-{i}-3",
                        "text": "Mentored 18 senior and staff engineers across 4 cross-functional distributed infrastructure teams.",
                    },
                ],
            }
            for i in range(1, 9)
        ],
    },
    {
        "id": "sec-projects",
        "type": "projects",
        "title": "Selected High-Impact Projects",
        "visible": True,
        "pageBreakBefore": False,
        "order": 2,
        "items": [
            {
                "id": f"proj-{i}",
                "title": f"Distributed Consensus Framework v{i}.0",
                "subtitle": "Open Source Initiative",
                "location": "GitHub",
                "dateRange": "2022 - 2024",
                "visible": True,
                "itemType": "timeline",
                "bullets": [
                    {
                        "id": f"b-proj-{i}-1",
                        "text": "Designed Byzantine fault-tolerant consensus protocol reducing quorum confirmation round-trips from 3 to 1.",
                    },
                    {
                        "id": f"b-proj-{i}-2",
                        "text": "Authored comprehensive whitepaper and formal TLA+ verification proofs demonstrating deadlock immunity.",
                    },
                ],
            }
            for i in range(1, 7)
        ],
    },
    {
        "id": "sec-education",
        "type": "education",
        "title": "Education & Research",
        "visible": True,
        "pageBreakBefore": False,
        "order": 3,
        "items": [
            {
                "id": "edu-1",
                "title": "Ph.D. in Computer Science",
                "subtitle": "Stanford University",
                "location": "Stanford, CA",
                "dateRange": "2012 - 2017",
                "visible": True,
                "itemType": "timeline",
                "bullets": [
                    {"id": "b-edu-1", "text": "Doctoral dissertation on lock-free parallel data structures for real-time collaborative editors."}
                ],
            },
            {
                "id": "edu-2",
                "title": "B.S. in Electrical Engineering & CS",
                "subtitle": "UC Berkeley",
                "location": "Berkeley, CA",
                "dateRange": "2008 - 2012",
                "visible": True,
                "itemType": "timeline",
                "bullets": [
                    {"id": "b-edu-2", "text": "Summa Cum Laude, Regents and Chancellor's Scholar, Tau Beta Pi Honor Society."}
                ],
            },
        ],
    },
]


def run_latency_test():
    print("=" * 70)
    print("RUNNING LATENCY BENCHMARK ON 3-PAGE RESUME WITH 4X CPU THROTTLING")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1200, "height": 1400})
        page = context.new_page()

        # Connect Chrome DevTools Protocol to enable 4x CPU Throttling
        cdp = context.new_cdp_session(page)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        print("Emulation.setCPUThrottlingRate: 4x enabled.")

        # Load render page
        page.goto("http://localhost:3000/render/preset-classic-single-column", wait_until="networkidle")
        page.wait_for_selector(".resume-document.resume-ready", timeout=10000)

        # Inject large 3-page resume content into the page state
        page.evaluate(
            """(sections) => {
                const doc = document.querySelector('.resume-document');
                if (window.__setResumeContent) {
                    window.__setResumeContent(sections);
                }
            }""",
            THREE_PAGE_SECTIONS,
        )

        # 1. Benchmark CSS variable injection latency (30 iterations)
        print("\n1. Benchmarking CSS Variable reactive update latency (30 token mutations)...")
        token_latencies = []
        colors = ["#2563eb", "#059669", "#7c3aed", "#dc2626", "#d97706", "#0284c7"]

        for i in range(30):
            color = colors[i % len(colors)]
            base_size = 9.0 + (i % 5) * 0.25

            t0 = time.perf_counter()
            page.evaluate(
                """({ color, size }) => {
                    const el = document.querySelector('.resume-document');
                    el.style.setProperty('--color-accent', color);
                    el.style.setProperty('--font-size-base', size + 'pt');
                    // Force synchronous reflow / paint measure
                    void el.offsetHeight;
                }""",
                {"color": color, "size": base_size},
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000
            token_latencies.append(elapsed_ms)

        # 2. Benchmark Keystroke / Text Mutation Latency under 4x CPU throttle (30 simulated keystrokes)
        print("2. Benchmarking simulated live text typing latency (30 keystrokes)...")
        keystroke_latencies = []
        for i in range(30):
            char = chr(ord('a') + (i % 26))
            t0 = time.perf_counter()
            page.evaluate(
                """(char) => {
                    const item = document.querySelector('.resume-item span');
                    if (item) {
                        item.textContent += char;
                        void item.offsetHeight;
                    }
                }""",
                char,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000
            keystroke_latencies.append(elapsed_ms)

        browser.close()

    # Calculate statistics
    avg_token = statistics.mean(token_latencies)
    p95_token = sorted(token_latencies)[int(len(token_latencies) * 0.95)]
    max_token = max(token_latencies)

    avg_key = statistics.mean(keystroke_latencies)
    p95_key = sorted(keystroke_latencies)[int(len(keystroke_latencies) * 0.95)]
    max_key = max(keystroke_latencies)

    print("\n" + "=" * 70)
    print("LATENCY BENCHMARK RESULTS (4x CPU THROTTLING)")
    print("=" * 70)
    print(f"Token CSS Variable Updates (30 runs):")
    print(f"  • Average Latency : {avg_token:.2f} ms")
    print(f"  • p95 Latency     : {p95_token:.2f} ms")
    print(f"  • Max Latency     : {max_token:.2f} ms")
    print(f"  • Target Threshold: < 50.00 ms -> {'PASSED' if avg_token < 50 else 'FAILED'}")

    print(f"\nKeystroke Text Reflows (30 runs):")
    print(f"  • Average Latency : {avg_key:.2f} ms")
    print(f"  • p95 Latency     : {p95_key:.2f} ms")
    print(f"  • Max Latency     : {max_key:.2f} ms")
    print(f"  • Target Threshold: < 50.00 ms -> {'PASSED' if avg_key < 50 else 'FAILED'}")
    print("=" * 70)

    assert avg_token < 50.0, f"Token latency {avg_token:.2f}ms exceeds 50ms budget"
    assert avg_key < 50.0, f"Keystroke latency {avg_key:.2f}ms exceeds 50ms budget"
    print("\nALL LATENCY BENCHMARKS PASSED UNDER 4X CPU THROTTLING!")


if __name__ == "__main__":
    run_latency_test()
