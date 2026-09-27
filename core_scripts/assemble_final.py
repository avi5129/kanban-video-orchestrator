#!/usr/bin/env python3
"""
assemble_final.py — Kanban Video Orchestrator final assembly script.

Concatenates scene clips in order using FFmpeg concat demuxer, then muxes
the master audio track. Produces output/final.mp4 and output/final_no_subs.mp4.

Usage:
  python assemble_final.py --workspace /path/to/project --scene-order 1 2 3 4 5 6 7
  python assemble_final.py --workspace /path/to/project --audio audio/track_final.wav

Dependencies:
  - ffmpeg at C:/Users/Avishkar/ffmpeg/ffmpeg.exe (Windows) or in PATH (Linux/macOS)
  - Python 3.8+
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# Windows ffmpeg path — adjust as needed
FFMPEG = shutil.which("ffmpeg") or r"C:/Users/Avishkar/ffmpeg/ffmpeg.exe"


def run_ffmpeg(args: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run ffmpeg with the given args. Prints command for debugging."""
    cmd = [FFMPEG] + args
    print(f"[ffmpeg] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # ffmpeg writes info to stderr — only print warnings/errors
        for line in result.stderr.splitlines():
            if line.startswith("["):
                print(f"[ffmpeg] {line}")
    if check and result.returncode != 0:
        print(f"[ERROR] ffmpeg failed with code {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result


def concat_scenes(workspace: Path, scene_order: list[int], output_clip: Path) -> None:
    """Concat scene clips in order using FFmpeg concat demuxer."""
    scene_dir = workspace / "scenes"
    concat_list = workspace / "scripts" / "_concat_list.txt"

    with open(concat_list, "w", encoding="utf-8") as f:
        for n in scene_order:
            clip_path = scene_dir / str(n) / "clip.mp4"
            if not clip_path.exists():
                print(f"[ERROR] Scene clip not found: {clip_path}", file=sys.stderr)
                sys.exit(1)
            # Write relative path for concat demuxer
            f.write(f"file '{clip_path.resolve()}'\n")

    print(f"[assemble] Concatenating {len(scene_order)} scenes -> {output_clip}")
    run_ffmpeg([
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(output_clip),
    ])


def mux_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    """Mux audio onto video. Video codec copy, audio re-encoded to AAC."""
    print(f"[assemble] Muxing audio={audio_path} onto video={video_path} -> {output_path}")
    run_ffmpeg([
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    ])


def verify_output(path: Path) -> dict:
    """Probe output file with ffprobe and return metadata."""
    result = subprocess.run(
        [FFMPEG, "-i", str(path), "-hide_banner"],
        capture_output=True, text=True,
    )
    # Parse basic info from ffprobe-style output
    info = {"path": str(path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}
    for line in result.stderr.splitlines():
        if "Duration:" in line:
            info["duration"] = line.split("Duration:")[1].split(",")[0].strip()
        if "Video:" in line:
            info["video"] = line.split("Video:")[1].split(",")[0].strip()
        if "Audio:" in line:
            info["audio"] = line.split("Audio:")[1].split(",")[0].strip()
    return info


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble final video from scene clips + master audio."
    )
    parser.add_argument(
        "--workspace", required=True, help="Path to project workspace"
    )
    parser.add_argument(
        "--scene-order", type=int, nargs="+", default=None,
        help="Scene numbers in order (e.g. 1 2 3 4 5 6 7). Defaults to all scenes found."
    )
    parser.add_argument(
        "--audio", default=None,
        help="Path to master audio WAV/MP4 relative to workspace (e.g. audio/track_final.wav)"
    )
    parser.add_argument(
        "--output-name", default="final.mp4",
        help="Output filename in output/ dir (default: final.mp4)"
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    output_dir = workspace / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine scene order
    if args.scene_order:
        scene_order = args.scene_order
    else:
        # Auto-detect: find all scene dirs with clip.mp4
        scene_dir = workspace / "scenes"
        scene_order = sorted(
            int(d.name) for d in scene_dir.iterdir()
            if d.is_dir() and (d / "clip.mp4").exists()
        )
        if not scene_order:
            print("[ERROR] No scene directories with clip.mp4 found.", file=sys.stderr)
            sys.exit(1)
        print(f"[assemble] Auto-detected scene order: {scene_order}")

    # Step 1: Concatenate scenes
    video_only = output_dir / "video_only.mp4"
    concat_scenes(workspace, scene_order, video_only)

    # Step 2: Mux audio if provided
    if args.audio:
        audio_path = (workspace / args.audio).resolve()
        if not audio_path.exists():
            print(f"[ERROR] Audio file not found: {audio_path}", file=sys.stderr)
            sys.exit(1)
        final = output_dir / args.output_name
        mux_audio(video_only, audio_path, final)

        # Also produce no-audio version
        no_subs = output_dir / "final_no_subs.mp4"
        shutil.copy2(video_only, no_subs)
        print(f"[assemble] No-audio version: {no_subs}")
    else:
        final = video_only
        print("[assemble] No audio specified — output is video only.")

    # Step 3: Verify
    info = verify_output(final)
    print(f"[assemble] Final deliverable: {info['path']}")
    print(f"[assemble]   Size: {info['size_bytes'] / 1024 / 1024:.2f} MB")
    if "duration" in info:
        print(f"[assemble]   Duration: {info['duration']}")
    if "video" in info:
        print(f"[assemble]   Video: {info['video']}")
    if "audio" in info:
        print(f"[assemble]   Audio: {info['audio']}")

    # Cleanup temp concat list
    concat_list = workspace / "scripts" / "_concat_list.txt"
    if concat_list.exists():
        concat_list.unlink()


if __name__ == "__main__":
    main()
