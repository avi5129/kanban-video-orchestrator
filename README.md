# Kanban Video Orchestrator

Kanban Video Orchestrator is a local, multi-agent AI framework built to design, render, and assemble short-form video content (9:16 Shorts/Reels) using specialized toolsets.

Rather than relying on a singular, monolithic automation script that yields rigid outputs, this framework uses a 7-agent production crew bound together by a deterministic Kanban workspace layout. It orchestrates complex mathematical animations (Manim), programmatic canvas art (p5.js), local high-fidelity speech synthesis (Qwen3-TTS), and low-level digital signal processing (SciPy/FFmpeg).

## The Multi-Agent Architecture

Every project initialized by the orchestrator assigns distinct roles to autonomous agent profiles, preventing context-drift and maintaining strict creative guardrails:

- **Director**: Decomposes the creative brief into discrete tasks and routes them via a dependency graph. Does not execute code.
- **Cinematographer**: Translates intent into scene-by-scene visual rules (VISUAL_SPEC.md), specifying tool constraints and timing.
- **Renderer**: Writes and executes code blocks per scene (generating Python scripts for Manim or Node.js/Puppeteer scripts to capture headless p5.js web components).
- **Voice-Talent**: Interacts with local execution wrappers to synthesize narration tracks using Qwen3-TTS 0.6B Base.
- **Audio-Mixer**: Executes programmatic audio engineers using SciPy and NumPy to mix music beds, voiceovers, and SFX.
- **Editor**: Executes low-level FFmpeg instructions to concatenate isolated scene clips, attach the master audio mix, and deliver the final render.
- **Reviewer**: Final QA agent verifying aspect ratios, track synchronization, resolution constraints, and file integrity.

## Standardized Project Anatomy

When a new project is bootstrapped, it structures a sandboxed environment on disk to enforce state management between independent rendering engines:

```
<project-slug>/
  ├── brief.md          # 1-sentence pitch, scope, and target deliverables
  ├── TEAM.md           # Active agent roster and task execution graphs (T0..T12)
  ├── plan.json         # Machine-readable project manifest (FPS, resolution, duration)
  ├── VISUAL_SPEC.md    # Global visual language and shot rules
  ├── audio/            # Raw sound assets, voiceover cuts, and master tracks
  ├── scenes/           # Sandboxed directories per scene containing individual venvs,
  │                     # index.html (p5.js), capture.js, and scene-specific Python files
  └── output/           # Render deliverables (final.mp4, final_no_subs.mp4)
```

## Tool Ecosystem

- **Visual Engines**: Manim Community Edition (utilizing MovingCameraScene for cinematic pans) and p5.js captured headlessly via Puppeteer.
- **Audio Pipeline**: Local Qwen3-TTS 0.6B Base for standard voice generation; SciPy, NumPy, and Pydub for math-driven multi-channel track mixing.
- **Compilation**: Raw system calls to local FFmpeg binaries for fast asset assembly.

## Installation (For Hermes Agent Users)

You can inject this orchestration capability directly into your local Hermes environment by referencing the skill sheet:

```bash
hermes skills install https://github.com/<your-username>/kanban-video-orchestrator
```

Or clone the skill into your local Hermes skills directory:

```bash
git clone https://github.com/<your-username>/kanban-video-orchestrator.git \
  ~/AppData/Local/hermes/skills/kanban-video-orchestrator
```

## Quick Start

1. **Scope the project**: Write a `brief.md` with your one-sentence pitch, duration, aspect ratio, and target platform.
2. **Bootstrap the workspace**: Run `core_scripts/bootstrap_pipeline.py` to auto-generate the full 7-agent directory tree, profile configs, and initial Kanban task.
3. **Launch the director**: The director profile decomposes the brief into a task graph (T0..T12) and routes work to specialist profiles via Kanban.
4. **Monitor execution**: Watch the Kanban board for task completion, review rendered clips, and intervene when tasks stall.

## What This Is Not

- This is **not** a cloud-based video rendering service.
- This is **not** a single-script automation that produces rigid, repetitive outputs.
- This is **not** a replacement for manual creative direction — the director profile enforces creative guardrails but the quality of the brief determines the quality of the output.

## What This Is

- A **deterministic workspace layout** that isolates each rendering engine's state (per-scene venvs, per-scene frame caches, isolated audio asset dirs).
- A **role-based multi-agent contract** that prevents any single agent from drifting into another's responsibilities.
- A **local-first toolchain** that runs Manim, p5.js/Puppeteer, Qwen3-TTS, SciPy, and FFmpeg on your own hardware — no API keys required for the core pipeline.
- A **proven scaffold** extracted from two completed productions (60s 9:16 cinematic shorts) with mixed Manim + p5.js scenes, local voice cloning, and multi-track audio mixing.

## Repository Structure

```
kanban-video-orchestrator/
├── README.md                 # This file
├── SKILL.md                  # Core system prompt & instructions for the Hermes Agent
├── LICENSE                   # MIT license
├── templates/                # Blueprint folders for new projects
│   ├── brief.md              # Template for creative pitch and project scoping
│   ├── TEAM.md               # Blueprint for the 7-agent role profiles and task graph
│   ├── plan.json             # Skeleton for machine-readable manifests
│   └── VISUAL_SPEC.md        # Standardized scene shot language template
├── core_scripts/             # Production pipeline automation utilities
│   ├── bootstrap_pipeline.py # Script to auto-generate the standard multi-agent directory tree
│   ├── assemble_final.py     # FFmpeg-based automated scene concatenation and audio muxing
│   └── generate_mix.py       # Custom SciPy-based multi-track audio mixer utility
└── references/               # Creative and execution standards
    ├── role-archetypes.md    # Detailed specifications for the 7 production profiles
    └── technical-stack.md    # Requirements for local dependencies (Manim, Qwen3-TTS, p5.js)
```

## License

MIT License — see LICENSE file for details.
