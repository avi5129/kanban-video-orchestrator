# Team & Task Graph — {PROJECT_TITLE}

## Team

- `director` — Read brief.md, TEAM.md, taste/. Decompose into the team graph. Route all work via kanban_create. Never execute scenes directly. (no skills required)
- `cinematographer` — Design visual language per scene: lighting, composition, transitions. Write VISUAL_SPEC.md for each scene. Review rendered clips. (loads `manim-video, p5js`)
- `renderer` — Render each scene per VISUAL_SPEC.md. Output scene clips to scenes/*/clip.mp4. (loads `manim-video, p5js`)
- `voice-talent` — Generate narration WAV files for each voiceover line. Output per-line WAV files to audio/voiceover/. (no skills required)
- `audio-mixer` — Mix music bed, voiceover, and SFX into audio/track.wav or audio/track_final.wav. (no skills required)
- `editor` — Concatenate scene clips, mux final audio, and verify output/final.mp4. (no skills required)
- `reviewer` — Final QA: verify duration, resolution, sync, and deliverable completeness. (no skills required)

## Task Graph

```
T0  director — decompose
T1    cinematographer — visual spec for all scenes (parent: T0)
T2    renderer — scene 1: {SCENE_1_DESC} (parents: T1)
T3    renderer — scene 2: {SCENE_2_DESC} (parents: T1)
T4    renderer — scene 3: {SCENE_3_DESC} (parents: T1)
T5    renderer — scene 4: {SCENE_4_DESC} (parents: T1)
T6    renderer — scene 5: {SCENE_5_DESC} (parents: T1)
T7    renderer — scene 6: {SCENE_6_DESC} (parents: T1)
T8    renderer — scene 7: {SCENE_7_DESC} (parents: T1)
T9    voice-talent — narration (parent: T0)
T10   audio-mixer — mix audio (parents: T9)
T11   editor — assemble + mux (parents: T2, T3, T4, T5, T6, T7, T8, T10, T9)
T12   reviewer — final QA (parent: T11)
```

## Per-task workspace requirement

All `kanban_create` calls MUST pass:

```
workspace_kind="dir"
workspace_path="$HOME/projects/video-pipeline/{PROJECT_SLUG}"
tenant="{PROJECT_SLUG}"
```

## Role toolsets

| Role | Toolsets | Skills |
|---|---|---|
| director | kanban, terminal, file | (none) |
| cinematographer | terminal, file | manim-video, p5js |
| renderer | terminal, file | manim-video, p5js |
| voice-talent | terminal, file | (none — uses local Qwen3-TTS) |
| audio-mixer | terminal, file | (none — uses SciPy/NumPy) |
| editor | terminal, file | (none — uses FFmpeg) |
| reviewer | terminal, file | (none) |
