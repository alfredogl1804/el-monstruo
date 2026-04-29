#!/usr/bin/env python3
"""
extract_clip.py - Extract a clip segment from a video/audio file.

Cuts a specific time range and optionally converts to TikTok-friendly format.

Usage:
  python3 extract_clip.py <input_file> <start_time> <end_time> <output_file> [--tiktok]

Arguments:
  input_file   : Path to source video/audio
  start_time   : Start time (seconds or HH:MM:SS format)
  end_time     : End time (seconds or HH:MM:SS format)
  output_file  : Path for output file
  --tiktok     : Optional flag to convert to TikTok vertical format (1080x1920)

Examples:
  python3 extract_clip.py music.mp4 15.5 30.0 clip.mp4
  python3 extract_clip.py music.mp4 0:15 0:30 clip.mp4 --tiktok
"""

import sys
import subprocess
import os

def extract_clip(input_file, start, end, output_file, tiktok_format=False):
    """Extract clip with ffmpeg."""

    cmd = ["ffmpeg", "-y", "-i", input_file, "-ss", str(start), "-to", str(end)]

    if tiktok_format:
        # Convert to 1080x1920 vertical format
        # Center-crop or pad to 9:16 aspect ratio
        cmd.extend([
            "-vf", (
                "scale=1080:1920:force_original_aspect_ratio=decrease,"
                "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
            ),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-r", "30",
            "-movflags", "+faststart"
        ])
    else:
        cmd.extend(["-c", "copy"])

    cmd.append(output_file)

    print(f"Extracting: {start} -> {end}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False

    if os.path.exists(output_file):
        size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"Output: {output_file} ({size:.1f} MB)")
        return True
    return False

def main():
    if len(sys.argv) < 5:
        print("Usage: python3 extract_clip.py <input> <start> <end> <output> [--tiktok]")
        sys.exit(1)

    input_file = sys.argv[1]
    start_time = sys.argv[2]
    end_time = sys.argv[3]
    output_file = sys.argv[4]
    tiktok = "--tiktok" in sys.argv

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    success = extract_clip(input_file, start_time, end_time, output_file, tiktok)
    if success:
        print("Done!")
    else:
        print("Failed to extract clip.")
        sys.exit(1)

if __name__ == "__main__":
    main()
