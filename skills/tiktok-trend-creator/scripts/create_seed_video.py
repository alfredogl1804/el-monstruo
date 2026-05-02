#!/usr/bin/env python3
"""
create_seed_video.py - Create a TikTok seed video with text overlays.

Takes a video/audio clip and adds text overlays synchronized with timestamps
to create the initial "seed" video that inspires a trend.

Usage:
  python3 create_seed_video.py <config_json> <output_file>

Config JSON structure:
{
  "input_file": "clip.mp4",
  "background_color": "black",
  "texts": [
    {
      "text": "When your partner says...",
      "start": 0.0,
      "end": 3.0,
      "position": "top",
      "fontsize": 60,
      "color": "white",
      "font": "Arial-Bold"
    },
    {
      "text": "POV: Date night gone wrong",
      "start": 0.0,
      "end": null,
      "position": "center_top",
      "fontsize": 48,
      "color": "yellow"
    }
  ],
  "width": 1080,
  "height": 1920
}

Position options: top, center_top, center, center_bottom, bottom, custom(x,y)
"""

import json
import os
import subprocess
import sys

# Position mapping for text placement (x, y expressions for ffmpeg drawtext)
POSITIONS = {
    "top": ("(w-text_w)/2", "80"),
    "center_top": ("(w-text_w)/2", "(h/4)"),
    "center": ("(w-text_w)/2", "(h-text_h)/2"),
    "center_bottom": ("(w-text_w)/2", "(3*h/4)"),
    "bottom": ("(w-text_w)/2", "h-text_h-120"),
}


def build_drawtext_filter(text_config, index):
    """Build a single drawtext filter string."""
    text = text_config["text"].replace("'", "\\'").replace(":", "\\:")
    start = text_config.get("start", 0)
    end = text_config.get("end")
    position = text_config.get("position", "center")
    fontsize = text_config.get("fontsize", 56)
    color = text_config.get("color", "white")
    font = text_config.get("font", "Sans-Bold")
    shadow_color = text_config.get("shadow_color", "black")
    border_w = text_config.get("border_w", 3)

    # Get position coordinates
    if position in POSITIONS:
        x, y = POSITIONS[position]
    elif "," in str(position):
        x, y = str(position).split(",")
    else:
        x, y = POSITIONS["center"]

    # Build enable expression
    if end is not None:
        enable = f"between(t,{start},{end})"
    else:
        enable = f"gte(t,{start})"

    # Drawtext filter with shadow for readability
    dt = (
        f"drawtext=text='{text}'"
        f":fontsize={fontsize}"
        f":fontcolor={color}"
        f":borderw={border_w}"
        f":bordercolor={shadow_color}"
        f":x={x}:y={y}"
        f":enable='{enable}'"
    )
    return dt


def create_seed_video(config, output_file):
    """Create the seed video using ffmpeg."""
    input_file = config["input_file"]
    width = config.get("width", 1080)
    height = config.get("height", 1920)
    texts = config.get("texts", [])

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return False

    # Build filter chain
    filters = []

    # Scale/pad to TikTok vertical format
    filters.append(
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color="
        f"{config.get('background_color', 'black')}"
    )

    # Add text overlays
    for i, text_cfg in enumerate(texts):
        dt = build_drawtext_filter(text_cfg, i)
        filters.append(dt)

    filter_str = ",".join(filters)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-vf",
        filter_str,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-r",
        "30",
        "-movflags",
        "+faststart",
        output_file,
    ]

    print(f"Creating seed video: {output_file}")
    print(f"Texts: {len(texts)} overlays")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr[-500:]}")
        return False

    if os.path.exists(output_file):
        size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"Success! Output: {output_file} ({size:.1f} MB)")
        return True

    return False


def create_audio_only_video(config, output_file):
    """Create video from audio-only input with colored background and text."""
    input_file = config["input_file"]
    width = config.get("width", 1080)
    height = config.get("height", 1920)
    bg_color = config.get("background_color", "black")
    texts = config.get("texts", [])

    # Get audio duration
    probe_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", input_file]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    duration = float(result.stdout.strip())

    # Build filter for text overlays
    text_filters = []
    for i, text_cfg in enumerate(texts):
        dt = build_drawtext_filter(text_cfg, i)
        text_filters.append(dt)

    text_chain = "," + ",".join(text_filters) if text_filters else ""

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={bg_color}:s={width}x{height}:d={duration}:r=30",
        "-i",
        input_file,
        "-vf",
        f"format=yuv420p{text_chain}",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-shortest",
        "-movflags",
        "+faststart",
        output_file,
    ]

    print(f"Creating video from audio with background: {output_file}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr[-500:]}")
        return False

    if os.path.exists(output_file):
        size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"Success! Output: {output_file} ({size:.1f} MB)")
        return True

    return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 create_seed_video.py <config.json> <output.mp4>")
        print("\nSee script header for config JSON structure.")
        sys.exit(1)

    config_path = sys.argv[1]
    output_file = sys.argv[2]

    with open(config_path) as f:
        config = json.load(f)

    # Check if input is audio-only
    probe_cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-show_streams",
        "-select_streams",
        "v",
        "-of",
        "csv=p=0",
        config["input_file"],
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    has_video = bool(result.stdout.strip())

    if has_video:
        success = create_seed_video(config, output_file)
    else:
        success = create_audio_only_video(config, output_file)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
