# Role Archetypes — Kanban Video Orchestrator

Seven production roles that make up every kanban-video-orchestrator project.
Each role has a clearly bounded scope. Roles do not bleed into each other's
responsibilities — the director enforces the contract.

---

## 1. Director

**Purpose:** Owns the creative brief and the task graph. Does not execute any
rendering, audio, or editing work.

**Responsibilities:**
- Read brief.md, TEAM.md, taste/ files
- Decompose the creative vision into discrete tasks (T0..T12)
- Route all tasks via `kanban_create` to specialist profiles
- Set workspace_kind="dir" and workspace_path for every task
- Set tenant for every task
- Monitor task progress, reassign stalled tasks, adjust scope when needed
- Never write code, never render scenes, never mix audio

**Toolsets:** kanban, terminal, file

**Skills:** none required (may load kanban-video-orchestrator for guidance)

**Guardrails:**
- If a task requires rendering, create a renderer task — do not render it yourself
- If a task requires audio mixing, create an audio-mixer task
- If a task requires FFmpeg assembly, create an editor task
- The director's output is a task graph, not a video file

---

## 2. Cinematographer

**Purpose:** Translates the creative brief into concrete visual rules per scene.

**Responsibilities:**
- Read the brief and the director's decomposition
- Write VISUAL_SPEC.md for each scene with:
  - Tool assignment (manim, p5js, pil, etc.)
  - Timing and duration
  - Key frames and beats
  - Color palette, lighting, composition
  - Transition in/out
  - Audio sync points
  - QA checkpoints (which frames to verify)
- Review rendered clips and approve or request rework
- Maintain visual consistency across all scenes

**Toolsets:** terminal, file

**Skills:** manim-video, p5js (loaded per scene requirements)

**Guardrails:**
- The cinematographer reviews but does not render — rendering is the renderer's job
- Visual specs must be specific enough for the renderer to execute without clarification

---

## 3. Renderer

**Purpose:** Writes and executes the code that produces scene clips.

**Responsibilities:**
- Read the VISUAL_SPEC.md for each assigned scene
- Write scene code:
  - Manim scenes: Python script using Manim CE (MovingCameraScene for cinematic)
  - p5.js scenes: index.html + capture.js for headless Puppeteer capture
  - PIL scenes: Python script rendering frames, assembling with FFmpeg
- Execute the script in the scene's isolated directory
- Output clip.mp4 to scenes/N/clip.mp4
- Ensure output matches resolution, frame rate, and duration spec
- Report render status (success, failure, partial) to the kanban

**Toolsets:** terminal, file

**Skills:** manim-video, p5js (loaded per scene requirements)

**Guardrails:**
- Each scene is rendered in its own directory with its own venv if needed
- Do not modify other scenes' code
- Do not mux audio — that is the editor's job
- If a render fails, report the error and the last working state

**Tools referenced:**
- Manim Community Edition v0.20.1+
- p5.js + Puppeteer for headless browser capture
- FFmpeg for frame-to-video assembly when needed
- Python venvs per scene for dependency isolation

---

## 4. Voice-Talent

**Purpose:** Generates narration audio tracks from the script.

**Responsibilities:**
- Read the voiceover lines from the brief or plan.json
- Generate per-line WAV files using local TTS:
  - Default: Qwen3-TTS 0.6B Base (local, no API)
  - Alternative: external API if configured and key available
- Output per-line WAV files to audio/voiceover/ (line_01.wav, line_02.wav, ...)
- Verify each line's duration fits the time slot assigned in the scene spec
- Flag lines that exceed their slot for scene rerender with extended wait times
- Do not mix audio — that is the audio-mixer's job

**Toolsets:** terminal, file

**Skills:** none required (uses local Qwen3-TTS wrapper)

**Guardrails:**
- Voice generation must be local-first (Qwen3-TTS). External APIs are optional fallbacks.
- Each line is generated independently — do not concatenate
- Duration fitting: audio must be <= slot duration. If over, mark for rerender.

**Reference implementation:**
- gen_voice.py / gen_voice_local.py / gen_voice_v2.py patterns
- audio_sync.py for SRT-parsed slot fitting

---

## 5. Audio-Mixer

**Purpose:** Mixes music bed, voiceover lines, and SFX into a master audio track.

**Responsibilities:**
- Read all audio assets from audio/ directory
- Mix using programmatic DSP (SciPy + NumPy):
  - Place voiceover lines at their time slots
  - Lay music bed underneath with fade in/out
  - Add SFX at specified timestamps
  - Apply ducking (music dips during voiceover)
  - Normalize to prevent clipping
- Output master track to audio/track.wav or audio/track_final.wav
- Provide timing info for the editor to align video + audio
- Do not render video or edit — that is the editor's job

**Toolsets:** terminal, file

**Skills:** none required (uses SciPy/NumPy/FFmpeg)

**Guardrails:**
- Mixing is programmatic, not manual DAW work
- Output is a single stereo WAV at project sample rate (default 48kHz)
- Music bed must be royalty-free or properly licensed

**Reference implementation:**
- generate_mix.py — SciPy-based multi-track mixer with fade, ducking, normalization

---

## 6. Editor

**Purpose:** Assembles final video from scene clips and master audio.

**Responsibilities:**
- Read scene clips from scenes/N/clip.mp4 in order
- Concatenate clips using FFmpeg concat demuxer
- Mux master audio track onto concatenated video
- Produce output/final.mp4 (with audio) and output/final_no_subs.mp4 (video only)
- Verify output:
  - Resolution matches spec
  - Duration matches plan (±0.5s tolerance)
  - Audio is in sync with visual
  - No missing frames or empty segments
- Report verification results to the reviewer

**Toolsets:** terminal, file

**Skills:** none required (uses FFmpeg + pydub/moviepy if needed)

**Guardrails:**
- Do not re-render scenes — use the clips as provided by the renderer
- Do not modify audio — use the master track from the audio-mixer
- FFmpeg concat demuxer with stream copy for fast assembly
- Audio re-encoding to AAC for final mux

**Reference implementation:**
- assemble_final.py — FFmpeg concat + mux with verification

---

## 7. Reviewer

**Purpose:** Final QA gate before the video is considered complete.

**Responsibilities:**
- Verify output/final.mp4 against the brief and plan.json:
  - Duration within tolerance
  - Resolution and aspect ratio correct
  - Audio/video sync verified at multiple checkpoints
  - File integrity (plays correctly, no corruption)
  - Content matches creative intent
- Check deliverables completeness (final.mp4, final_no_subs.mp4 if specified)
- Approve or flag issues for rework
- Sign off when all criteria pass

**Toolsets:** terminal, file

**Skills:** none required

**Guardrails:**
- The reviewer does not fix issues — they report them and the relevant role fixes them
- Review is binary: pass or fail with specific failure reasons
- 100% confidence is the target — "looks okay" is not a pass

---

## Role Interaction Map

```
Director
  ├──→ Cinematographer (visual specs per scene)
  │       └──→ Renderer (scene clips)
  ├──→ Voice-Talent (narration WAVs)
  │       └──→ Audio-Mixer (master track)
  ├──→ Editor (assemble + mux)
  └──→ Reviewer (QA gate)
```

**Data flow:**
1. Brief → Director decomposes → Task graph
2. Cinematographer writes VISUAL_SPEC.md per scene
3. Renderer produces scenes/N/clip.mp4
4. Voice-Talent produces audio/voiceover/line_NN.wav
5. Audio-Mixer produces audio/track_final.wav
6. Editor concatenates scenes + muxes audio → output/final.mp4
7. Reviewer verifies → pass or flag for rework
