# Technical Stack — Kanban Video Orchestrator

Local dependencies required to run the full pipeline. All tools run on-device —
no cloud rendering, no mandatory API keys for the core pipeline.

---

## Core Dependencies

### FFmpeg (mandatory)
- **Purpose:** Video assembly, audio muxing, format conversion
- **Version:** Any recent build (4.x or 5.x)
- **Windows path:** `C:\Users\Avishkar\ffmpeg\ffmpeg.exe` (also in PATH)
- **Linux/macOS:** `ffmpeg` in PATH
- **Used by:** Editor (assemble_final.py), Renderer (frame assembly), Audio-Mixer (format conversion)

### Python 3.8+
- **Purpose:** All pipeline scripts, Manim, audio processing, bootstrap
- **Packages:**
  - `numpy` — audio DSP arrays
  - `scipy` — WAV I/O, signal processing
  - `pydub` — audio segment manipulation (optional, used by some mux scripts)
  - `moviepy` — video/audio clip manipulation (optional)
  - `pyyaml` — plan.json parsing (if YAML configs used)
- **Per-scene venvs:** Each scene may have its own virtualenv for dependency isolation

### Manim Community Edition (for Manim scenes)
- **Package:** `manim` (community edition)
- **Version:** 0.20.1+ (MovingCameraScene support required for cinematic pans)
- **Backend:** OpenGL (for GPU acceleration) or Cairo (CPU fallback)
- **Used by:** Renderer for Manim-assigned scenes
- **Notes:**
  - `MovingCameraScene` is the base class for cinematic camera movements
  - `self.camera.frame.save_state()` / `self.camera.frame.animate` for zoom/pan
  - `self.add_subcaption()` for SRT-ready subtitle generation
  - Output: partial_movie_files/ (manim render cache) + final .mp4

### p5.js + Puppeteer (for p5.js scenes)
- **p5.js:** JavaScript creative coding library for canvas-based animation
- **Puppeteer:** Headless Chromium for capturing p5.js animation frames
- **Used by:** Renderer for p5js-assigned scenes
- **Workflow:**
  1. Write `index.html` with p5.js sketch
  2. Write `capture.js` with Puppeteer script to capture frames
  3. Run `capture.js` to produce frames/ directory
  4. Assemble frames into clip.mp4 with FFmpeg
- **Notes:**
  - Puppeteer needs a local Chromium install (puppeteer npm package bundles one)
  - 9:16 canvas: 1080x1920 pixels
  - 30fps capture: one frame every 33.3ms

### Qwen3-TTS 0.6B Base (for voice-talent)
- **Package:** `qwen-tts` (or `qwen3-tts`)
- **Version:** 0.1.1+ (or latest available)
- **Model:** Qwen3-TTS-12Hz-0.6B-Base (local, no API)
- **Device:** CUDA (RTX 3050 6GB or better) or CPU fallback
- **Used by:** Voice-Talent for narration generation
- **Notes:**
  - Voice clone mode: `generate_voice_clone(..., x_vector_only_mode=True)` with reference WAV + reference text
  - Reference pair: ref.wav + ref.txt (e.g. "Hello! my name is Avishkar")
  - No FlashAttention2 required for 0.6B model
  - Language must be full name (e.g. "English"), not "en"
  - Per-line generation: each narration line generated independently
  - Duration fitting: if audio > slot, mark for scene rerender with extended self.wait()

### scipy + numpy (for audio-mixer)
- **Purpose:** Multi-track audio mixing, DSP operations
- **Used by:** generate_mix.py — the canonical mixer script
- **Operations:**
  - wav_to_mono(): convert any WAV to mono at target SR via FFmpeg
  - to_stereo(): duplicate mono to stereo
  - fade(): linear fade in/out
  - softmax(): level normalization across tracks
  - mix_tracks(): sum tracks with start offsets
  - write_stereo_wav(): 16-bit PCM output

---

## Optional Dependencies

### Pydub
- **Purpose:** High-level audio segment manipulation
- **Used by:** Some mux scripts (the-last-frame mux scripts use pydub)
- **Alternative to:** Manual SciPy mixing

### MoviePy
- **Purpose:** Video/audio clip manipulation, simple muxing
- **Used by:** Early mux attempts (mux_moviepy.py)
- **Note:** Slower than direct FFmpeg for assembly — concat demuxer preferred

### PyTorch
- **Purpose:** Required by Qwen3-TTS and Manim OpenGL backend
- **Version:** 2.x with CUDA support
- **Used by:** Voice-Talent (Qwen3-TTS), Renderer (Manim OpenGL)

### Chromium / Chrome
- **Purpose:** Puppeteer headless browser for p5.js capture
- **Used by:** Renderer for p5js scenes
- **Install:** `npm install puppeteer` bundles a compatible Chromium

---

## System Requirements

### Minimum
- CPU: 4+ cores
- RAM: 8GB (16GB recommended for Manim + PyTorch concurrently)
- Storage: 50GB free (Manim partial renders, frame caches, voice model)
- OS: Windows 10/11, Linux, macOS

### Recommended
- GPU: CUDA-capable (RTX 3050 6GB or better for Qwen3-TTS voice clone)
- RAM: 16GB+
- Storage: 100GB+ SSD (frame caches and partial renders are I/O heavy)
- ffmpeg in PATH or at known location

---

## Workspace Layout (per project)

```
<project-slug>/
  brief.md              — creative pitch (filled by director from template)
  TEAM.md               — 7-agent roster + task graph (filled from template)
  plan.json             — machine-readable manifest (filled from template)
  VISUAL_SPEC.md        — global visual language (filled by cinematographer from template)
  audio/
    voiceover/          — line_01.wav, line_02.wav, ... (from voice-talent)
    music_bed.wav       — royalty-free music bed
    sfx/                — bass_impact.wav, pulse.wav, etc.
    track.wav           — mixed audio (from audio-mixer)
    track_final.wav     — final mixed audio
  scenes/
    N/                  — one dir per scene (N = 1, 2, 3, ...)
      clip.mp4          — rendered scene clip (from renderer)
      render.py         — manim render script (manim scenes)
      render_sceneN.py  — PIL/p5js render script (non-manim scenes)
      capture.js        — p5js Puppeteer capture script
      index.html        — p5js sketch page
      frames/           — rendered frame images (p5js scenes)
      frame-qa.png      — QA checkpoint frame
      VISUAL_SPEC.md    — per-scene visual spec
      __pycache__/      — Python cache (manim scenes)
      .venv/            — optional per-scene virtualenv
  output/
    final.mp4           — primary deliverable (from editor)
    final_no_subs.mp4   — alternate without subtitles (from editor)
    qa_frame_*.png      — QA snapshots at various timestamps
  scripts/
    bootstrap_pipeline.py   — project generator (from core_scripts/)
    assemble_final.py       — FFmpeg concat + mux (from core_scripts/)
    generate_mix.py         — SciPy audio mixer (from core_scripts/)
  taste/
    brand-guide.md       — brand colors, typography, logos
    emotional-dna.md     — emotional arc definition
```

---

## Audio Pipeline (reference flow)

1. **Voice-Talent** generates per-line WAVs → `audio/voiceover/line_NN.wav`
2. **Audio-Mixer** runs `generate_mix.py`:
   - Loads music bed
   - Loads voiceover lines
   - Loads SFX
   - Places each at correct time offset
   - Applies ducking, fade, normalization
   - Writes `audio/track_final.wav`
3. **Editor** runs `assemble_final.py`:
   - Concatenates scene clips via FFmpeg concat demuxer
   - Muxes `audio/track_final.wav` onto video
   - Produces `output/final.mp4`

**Sample rate:** 48000 Hz (default, configurable in generate_mix.py SR variable)

---

## Video Pipeline (reference flow)

1. **Cinematographer** writes VISUAL_SPEC.md per scene
2. **Renderer** executes per scene:
   - Manim scene: `manim render scene.py SceneN --resolution 1080x1920`
   - p5js scene: `node capture.js` → frames → FFmpeg → clip.mp4
   - Output: `scenes/N/clip.mp4`
3. **Editor** runs `assemble_final.py`:
   - FFmpeg concat demuxer: `scenes/1/clip.mp4` + `scenes/2/clip.mp4` + ...
   - Stream copy (no re-encode) for speed
   - Mux audio track with AAC encoding
   - Output: `output/final.mp4`

**Resolution:** 1080x1920 (9:16 vertical) — default, configurable per project
**Frame rate:** 30fps — default, 60fps for high-motion Manim scenes
