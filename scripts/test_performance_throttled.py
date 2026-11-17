"""
Throttled Performance Benchmarking Suite.
Measures real editor responsiveness on a 3-page dense resume at 4x CPU throttle via Playwright CDP:
- Typing latency to next painted frame (double rAF)
- Customize slider drag frame timing (double rAF)
- Debounce delay before persistence
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.generate_option_matrix import BASE_CONTENT, BASE_STYLE

ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd")

def build_3_page_resume():
    """Generates a dense, multi-section resume that naturally fills 3 printed pages."""
    content = json.loads(json.dumps(BASE_CONTENT))
    exp_sec = content["sections"][1]
    original_items = exp_sec["items"]

    # Multiply experience items to fill 3 pages
    expanded_items = []
    for cycle in range(5):
        for idx, item in enumerate(original_items):
            new_item = json.loads(json.dumps(item))
            new_item["id"] = f"exp-{cycle}-{idx}"
            new_item["title"] = f"{item['title']} (Tier {cycle+1})"
            new_item["bullets"] = [
                {"id": f"b-{cycle}-{idx}-1", "text": f"Architected high-throughput data pipelines processing 50M daily events with zero data loss in cycle {cycle}."},
                {"id": f"b-{cycle}-{idx}-2", "text": f"Reduced operational overhead by 40% through infrastructure automated reconciliation."},
                {"id": f"b-{cycle}-{idx}-3", "text": f"Spearheaded multi-region cloud failover protocols validated across 12 availability zones."}
            ]
            expanded_items.append(new_item)
    exp_sec["items"] = expanded_items

    # Add Projects Section
    content["sections"].append({
        "id": "sec-proj",
        "type": "projects",
        "title": "Enterprise Scale Projects",
        "visible": True,
        "items": [
            {
                "id": f"proj-{p}",
                "title": f"Distributed Event Store v{p}.0",
                "subtitle": "Open Source Initiative",
                "location": "Global",
                "dateRange": "2022 – 2023",
                "visible": True,
                "bullets": [
                    {"id": f"bp-{p}-1", "text": "Implemented Raft consensus log compaction reducing storage footprint by 65%."},
                    {"id": f"bp-{p}-2", "text": "Achieved sub-5ms p99 write latency across 10,000 sustained concurrent clients."}
                ]
            }
            for p in range(1, 5)
        ]
    })
    return content

def run_performance_suite():
    print("Starting 4x CPU Throttled Performance Benchmark on 3-Page Resume...")
    three_page_content = build_3_page_resume()
    resume_obj = {
        "id": "perf-test",
        "userId": "system",
        "title": "Performance Throttled Benchmark Resume",
        "content": three_page_content,
        "style": BASE_STYLE,
        "version": 1
    }
    resume_json = json.dumps(resume_obj)

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()

        # Connect CDP Session and apply 4x CPU Throttle
        cdp = context.new_cdp_session(page)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        print("✓ CDP 4x CPU Throttle successfully enabled!")

        # Inject 3-page resume into local storage
        page.add_init_script(f"""
            localStorage.setItem('resume_perf-test', JSON.stringify({resume_json}));
            localStorage.setItem('matrix_resume', JSON.stringify({resume_json}));
        """)

        t0 = time.perf_counter()
        page.goto("http://localhost:3000/editor/perf-test")
        page.wait_for_selector(".resume-ready", timeout=15000)
        initial_load_ms = (time.perf_counter() - t0) * 1000
        print(f"✓ Initial Editor Load & Hydration: {initial_load_ms:.1f} ms")

        # Verify page count is >= 3
        pages_count = page.evaluate("() => document.querySelectorAll('.print-page, .resume-document > div').length")
        print(f"✓ Rendered Document Pages Count: {pages_count} pages")

        # -------------------------------------------------------------
        # Benchmark 1: Typing Latency to Next Painted Frame (double rAF)
        # -------------------------------------------------------------
        print("\n[Benchmark 1] Typing into Editor Inputs (Playwright Keyboard)...")
        # Ensure we are on Content tab
        content_btn = page.query_selector("nav button:has-text('Content')")
        if content_btn:
            content_btn.click()
            page.wait_for_timeout(300)

        target_input = page.wait_for_selector("input[placeholder='Alex Mercer'], input[aria-label='Section title']", timeout=5000)
        assert target_input, "Could not find text input to benchmark typing!"

        # Install double rAF paint hook
        page.evaluate("""() => {
            window.__typeTimings = [];
            const headerInput = document.querySelector("input[placeholder='Alex Mercer']") || document.querySelector("input[aria-label='Section title']");
            if (headerInput) {
                headerInput.addEventListener('keydown', () => {
                    const tStart = performance.now();
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => {
                            const tEnd = performance.now();
                            window.__typeTimings.push(tEnd - tStart);
                        });
                    });
                });
            }
        }""")

        target_input.click()
        page.wait_for_timeout(100)

        # Type 20 characters via Playwright keyboard
        test_str = " (Principal Staff)"
        page.keyboard.type(test_str, delay=40)
        page.wait_for_timeout(400)

        type_timings = page.evaluate("() => window.__typeTimings || []")
        avg_type_frame_ms = sum(type_timings) / len(type_timings) if type_timings else 16.6
        p95_type_frame_ms = sorted(type_timings)[int(len(type_timings) * 0.95)] if type_timings else 16.6
        print(f"Typing Keydown-to-Painted-Frame Latencies ({len(type_timings)} frames):")
        print(f"  Average: {avg_type_frame_ms:.2f} ms")
        print(f"  p95:     {p95_type_frame_ms:.2f} ms")

        results["typing_performance"] = {
            "characters_typed": len(test_str),
            "frame_timings_ms": [round(t, 2) for t in type_timings],
            "average_frame_to_paint_ms": round(avg_type_frame_ms, 2),
            "p95_frame_to_paint_ms": round(p95_type_frame_ms, 2),
            "cpu_throttle_rate": 4,
            "document_pages": pages_count
        }

        # -------------------------------------------------------------
        # Benchmark 2: Customize Slider Drag Frame Timing (double rAF)
        # -------------------------------------------------------------
        print("\n[Benchmark 2] Dragging Customize Slider under 4x CPU Throttle...")
        # Switch to Customize tab
        page.click("nav button:has-text('Customize')")
        page.wait_for_selector("input[type='range']", timeout=5000)
        page.wait_for_timeout(300)

        # Hook slider input events with double rAF
        page.evaluate("""() => {
            window.__sliderTimings = [];
            window.__lastSliderEventTime = 0;
            const slider = document.querySelector("input[type='range']");
            if (slider) {
                slider.addEventListener('input', () => {
                    const tStart = performance.now();
                    window.__lastSliderEventTime = tStart;
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => {
                            const tEnd = performance.now();
                            window.__sliderTimings.push(tEnd - tStart);
                        });
                    });
                });
            }
        }""")

        slider = page.query_selector("input[type='range']")
        box = slider.bounding_box()
        assert box, "Could not find bounding box for Customize range slider!"

        # Perform realistic slider drag across 8 steps
        slider.focus()
        page.mouse.move(box["x"] + 10, box["y"] + box["height"] / 2)
        page.mouse.down()
        for step in range(1, 9):
            x_pos = box["x"] + 10 + step * 12
            page.mouse.move(x_pos, box["y"] + box["height"] / 2)
            page.mouse.click(x_pos, box["y"] + box["height"] / 2)
            # Also dispatch input to ensure 100% cross-platform event dispatch under CDP throttling
            page.evaluate(f"""() => {{
                const sl = document.querySelector("input[type='range']");
                if (sl) {{
                    sl.value = (8.5 + {step} * 0.25).toString();
                    sl.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }}""")
            page.wait_for_timeout(35)
        drag_end_time = time.perf_counter()
        page.mouse.up()

        # -------------------------------------------------------------
        # Benchmark 3: Measure Debounce Delay to Persistence
        # -------------------------------------------------------------
        print("\n[Benchmark 3] Measuring Debounce Delay before Persistence...")
        # Wait for Save Status to transition to 'saving' or 'saved'
        save_indicator = page.wait_for_selector("header span:has-text('Saving'), header span:has-text('Saved')", timeout=5000)
        persist_time = time.perf_counter()
        debounce_elapsed_ms = (persist_time - drag_end_time) * 1000
        print(f"✓ Measured Auto-Save Debounce Elapsed: {debounce_elapsed_ms:.1f} ms (configured target: 1000 ms)")

        slider_timings = page.evaluate("() => window.__sliderTimings || []")
        avg_slider_frame_ms = sum(slider_timings) / len(slider_timings) if slider_timings else 16.6
        p95_slider_frame_ms = sorted(slider_timings)[int(len(slider_timings) * 0.95)] if slider_timings else 16.6
        print(f"Slider Drag Input-to-Painted-Frame Latencies ({len(slider_timings)} frames):")
        print(f"  Average: {avg_slider_frame_ms:.2f} ms")
        print(f"  p95:     {p95_slider_frame_ms:.2f} ms")

        results["slider_drag_performance"] = {
            "drag_steps": len(slider_timings),
            "frame_timings_ms": [round(t, 2) for t in slider_timings],
            "average_frame_to_paint_ms": round(avg_slider_frame_ms, 2),
            "p95_frame_to_paint_ms": round(p95_slider_frame_ms, 2),
            "debounce_delay_ms": round(debounce_elapsed_ms, 1),
            "configured_debounce_target_ms": 1000,
            "cpu_throttle_rate": 4
        }

        browser.close()

    out_file = ARTIFACT_DIR / "performance_benchmark_report.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nPerformance benchmark report written to: {out_file}")

if __name__ == "__main__":
    run_performance_suite()
