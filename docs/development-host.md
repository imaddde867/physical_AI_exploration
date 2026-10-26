# Development machine — MacBook Pro 14-inch, base M4 (2024)

**Reference: owner-provided hardware specification document, dated 2026-10-26.** This is a machine *model/profile* specification, not a live diagnostic snapshot and not a local model performance benchmark.

| Item | Verified profile | Consequence for this repository |
|---|---|---|
| Model | 14-inch MacBook Pro (2024), **Mac16,1**, **base M4** (not Pro/Max) | Apple Silicon / ARM64 native tools |
| CPU | **10 cores: 4 performance + 6 efficiency** | Python, PlatformIO, CAD and serial tasks run locally |
| GPU | **10-core integrated M4**, Metal | Optional future MLX workloads only |
| Memory | **16 GB unified** CPU/GPU/system pool | Not 16 GB of dedicated VRAM; keep system and browser responsive |
| Advertised peak bandwidth | **120 GB/s** | Not a sustained benchmark guarantee |
| Neural Engine | 16 cores, advertised **38 TOPS peak** | Not a claim about LLM tokens/sec; MLX uses Metal GPU for standard inference |
| Ports | **3 Thunderbolt 4 / USB-C** | Only an ordinary **data-capable USB cable** is needed for ESP32 serial |
| Current installed macOS | **Unknown from attached profile** | Check actual OS and tool versions on the laptop |
| Actual internal SSD capacity | **Unknown from attached profile** | Do not prescribe arbitrary storage budgets |

## Development choices

1. **V0 — no local ML:** use Python 3.12 and PlatformIO on Apple Silicon; run tests and the USB serial controller. There is **no need to download any model** or use the RTX 5060 Ti / RTX 5090.
2. **V1 — embedded validation:** compile both ESP32-S3 N16R8 profiles, flash only the one matching the physical USB connector, inspect the 240×240 face visually, then measure real sensor/serial behavior.
3. **V2 — optional Mac-local intelligence:** prefer a small model that fits alongside macOS and normal applications; start with an allowlisted face-action interface. Report real time-to-first-token, tokens/s, RAM/swap, p50/p95 command latency, battery use and action errors. Do **not** infer model fit from a fictional 16 GB VRAM pool.
4. **Printing:** OpenSCAD and Bambu Studio are separate CAD/slicer tasks. Check the actual printer model before choosing a profile. 3D printing and the embedded build are independent of local ML.

**Do not assume:** user's SSD size, macOS release, installed Python version, display finish, battery health or exact available Metal allocation. None of these was established by the attached document.

References: [owner's model/specification source](https://support.apple.com/en-us/121552), [MacBook model identification](https://support.apple.com/en-us/108052), [Mac bootstrap](clone-and-run.md).
