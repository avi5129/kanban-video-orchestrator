name: kanban-video-orchestrator
description: >
  Multi-agent video production pipeline for Hermes Agent. Decomposes video
  creation into 7 specialized roles (director, cinematographer, renderer,
  voice-talent, audio-mixer, editor, reviewer) coordinated through a Kanban
  workspace. Renders short-form 9:16 video using Manim, p5.js/Puppeteer,
  Qwen3-TTS, SciPy, and FFmpeg — all local, no cloud APIs required.
version: 1.0.0
author: avi5129
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, kanban, multi-agent, orchestration, production-pipeline, manim, p5js, tts, ffmpeg]
    related_skills: []
    credits: >
      Extracted from two completed 60-second 9:16 cinematic productions
      built via Hermes Kanban multi-agent pipeline. The workspace layout,
      profile-config patching pattern, SOUL.md-per-profile model, TEAM.md
      task-graph convention, and `--workspace dir:<path>` discipline are
      adapted from the original kanban-video-pipeline at
      https://github.com/NousResearch/kanban-video-pipeline.
---

# Kanban Video Orchestrator — Skill

Wrap any video request in a Hermes Kanban pipeline that decomposes the work
to specialized agent profiles.

This skill does NOT render anything itself. It is a meta-pipeline that:

1. Scopes the request through targeted discovery
2. Designs an appropriate team (which roles, which tools per role)
3. Generates a setup script that creates Hermes profiles, project workspace, and the initial kanban task
4. Hands off to the director profile, which decomposes via the kanban
5. Monitors execution, helps intervene when tasks stall or fail

The actual rendering happens inside the kanban once it's running, via whichever
existing skills + tools fit the scenes — manim-video, p5js, comfyui, or plain
Python with PIL + ffmpeg.

## When NOT to use this skill

- The video is one continuous procedural project that needs no specialists.
  Just write the code directly.
- The user wants a quick one-shot conversion (e.g. convert mp4 to GIF) — use ffmpeg directly.
- The output is a static image, GIF, or audio-only artifact — use the matching specific skill.
- The work fits a single existing skill cleanly (e.g. a pure ASCII video — just use ascii-video).

## Workflow

DISCOVER → BRIEF → TEAM DESIGN → SETUP → EXECUTE → MONITOR

### Step 1 — Discover

Always start with three questions:
- What is the video? (one-sentence brief)
- How long? (5-30s teaser / 30-90s short / 90s-3min explainer / 3-10min film / longer)
- What aspect ratio + target platform? (1:1 / 9:16 / 16:9; X, IG, YouTube, internal, etc.)

From the answer, classify the style category and ask follow-ups. Do not ask all
questions at once. Make reasonable assumptions when the user implies an answer.

### Step 2 — Brief

Once enough is known, produce a structured `brief.md`:

1. Concept — one-sentence pitch + emotional north star
2. Scope — duration, aspect, platform, deadline
3. Style — visual references, brand constraints, tone
4. Scenes — beat-by-beat breakdown (durations, content, target tool)
5. Audio — narration / music / SFX / silent (per scene if needed)
6. Deliverables — file format, resolution, optional alternates

Show the brief to the user for confirmation before designing the team.
The brief is the contract — every downstream task references it.

### Step 3 — Team design

Pick role archetypes from the library that fit this video. Most videos need
4-7 profiles. The director is always present; the rest are picked by what the
brief actually requires.

See `references/role-archetypes.md` for the role library.

### Step 4 — Setup

Generate a setup script and run it. The script:

1. Creates the project workspace (`~/projects/video-pipeline/<slug>/`)
2. Copies any provided assets into `taste/`, `audio/`, `assets/`
3. Creates each Hermes profile via `hermes profile create --clone`
4. Writes per-profile `SOUL.md` (personality + role definition)
5. Configures profile YAML (toolsets, always_load skills, cwd)
6. Writes `brief.md`, `TEAM.md`, and `taste/` content
7. Fires the initial `hermes kanban create` task assigned to the director

Use `core_scripts/bootstrap_pipeline.py` to generate the setup from a brief +
team-design JSON.

### Step 5 — Execute

Run the setup script. Then provide the user with monitoring commands:

```bash
hermes kanban watch --tenant <project-tenant>     # live events
hermes kanban list  --tenant <project-tenant>     # board snapshot
```

The director profile takes over from here, decomposing the work and routing
tasks to specialist profiles via the kanban toolset.

### Step 6 — Monitor and intervene

Stay engaged — the kanban runs autonomously but a stuck task or bad output
needs human (or AI) judgment.

When a worker's output fails review:
1. Comment on the worker's task with specific feedback
2. Create a re-run task with the original as parent
3. Adjust the brief's scope and let the director re-decompose

## Critical rules

1. **Discovery before action.** Never start generating a brief or team without
   asking at least the three baseline questions.
2. **Match the team to the video.** Don't reuse the same 4-profile setup for
   every job.
3. **One workspace per project.** All profiles for a given video share the same
   `dir:` workspace. Every `kanban_create` call passes
   `workspace_kind="dir"` + `workspace_path="<absolute project path>"`.
4. **Tenant every project.** Use a project-specific tenant to keep the dashboard
   scoped and prevent cross-pollination.
5. **Respect existing skills.** When a scene fits an existing skill, the renderer
   should load that skill. Do not re-derive what a skill already provides.
6. **The director never executes.** The director decomposes and routes only —
   every concrete task becomes a kanban create call to a specialist profile.
7. **Don't over-decompose.** A 30-second product video does NOT need 20 tasks.
8. **Verify API keys BEFORE firing.** External APIs need keys in the secret store.
   A worker that hits a missing-key error wastes a task slot.

## File map

```
SKILL.md                            ← this file
templates/
  brief.md.tmpl                     ← brief skeleton
  TEAM.md.tmpl                     ← team + task graph skeleton
  plan.json.tmpl                   ← machine-readable manifest skeleton
  VISUAL_SPEC.md.tmpl             ← per-scene visual spec skeleton
core_scripts/
  bootstrap_pipeline.py            ← generate project tree from brief + team JSON
  assemble_final.py               ← FFmpeg concat + mux
  generate_mix.py                 ← SciPy multi-track audio mixer
references/
  role-archetypes.md               ← role library (7 profiles)
  technical-stack.md               ← local deps: Manim, Qwen3-TTS, p5.js, FFmpeg
```
