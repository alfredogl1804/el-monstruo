#!/usr/bin/env python3
"""
analyze_song.py - Analyze a music video/audio file.

Extracts:
  - Duration
  - Audio properties (sample rate, channels, bitrate)
  - Beat timestamps (approximate via volume peaks)
  - Generates a waveform visualization

Usage:
  python3 analyze_song.py <input_video_or_audio> [output_dir]

Output:
  - analysis.json with metadata and beat info
  - waveform.png visualization
"""

import json
import os
import subprocess
import sys
import tempfile


def get_media_info(filepath):
    """Extract media info using ffprobe."""
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running ffprobe: {result.stderr}")
        sys.exit(1)
    return json.loads(result.stdout)


def extract_audio(filepath, output_path):
    """Extract audio track to WAV for analysis."""
    cmd = ["ffmpeg", "-y", "-i", filepath, "-vn", "-acodec", "pcm_s16le", "-ar", "22050", "-ac", "1", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def analyze_beats_simple(wav_path):
    """Simple beat detection using volume envelope peaks."""
    try:
        import wave

        import numpy as np

        with wave.open(wav_path, "r") as wf:
            sr = wf.getframerate()
            n_frames = wf.getnframes()
            audio_data = wf.readframes(n_frames)

        samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        samples = samples / (np.max(np.abs(samples)) + 1e-8)

        # Compute energy envelope with hop size
        hop = int(sr * 0.01)  # 10ms hops
        window = int(sr * 0.05)  # 50ms window
        energy = []
        for i in range(0, len(samples) - window, hop):
            energy.append(np.sqrt(np.mean(samples[i : i + window] ** 2)))
        energy = np.array(energy)

        # Find peaks (simple onset detection)
        threshold = np.mean(energy) + 1.5 * np.std(energy)
        min_distance = int(0.3 / 0.01)  # minimum 300ms between beats

        beats = []
        last_beat = -min_distance
        for i in range(1, len(energy) - 1):
            if (
                energy[i] > energy[i - 1]
                and energy[i] > energy[i + 1]
                and energy[i] > threshold
                and (i - last_beat) >= min_distance
            ):
                beat_time = round(i * 0.01, 3)
                beats.append(beat_time)
                last_beat = i

        return {
            "sample_rate": sr,
            "duration_seconds": round(len(samples) / sr, 2),
            "total_samples": len(samples),
            "estimated_beats": beats[:100],  # limit to first 100
            "beat_count": len(beats),
            "avg_energy": round(float(np.mean(energy)), 4),
            "peak_energy": round(float(np.max(energy)), 4),
        }
    except Exception as e:
        return {"error": str(e)}


def generate_waveform(wav_path, output_png, duration=None):
    """Generate waveform image using ffmpeg."""
    filters = "showwavespic=s=1200x200:colors=#4ECDC4"
    if duration:
        filters = "showwavespic=s=1200x200:colors=#4ECDC4"
    cmd = ["ffmpeg", "-y", "-i", wav_path, "-filter_complex", filters, "-frames:v", "1", output_png]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_song.py <input_file> [output_dir]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(input_file) or "."

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Analyzing: {input_file}")

    # Get media info
    info = get_media_info(input_file)
    fmt = info.get("format", {})
    streams = info.get("streams", [])

    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)

    analysis = {
        "input_file": os.path.basename(input_file),
        "duration": float(fmt.get("duration", 0)),
        "format": fmt.get("format_long_name", "unknown"),
        "has_video": video_stream is not None,
        "has_audio": audio_stream is not None,
    }

    if video_stream:
        analysis["video"] = {
            "codec": video_stream.get("codec_name"),
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "fps": video_stream.get("r_frame_rate"),
        }

    if audio_stream:
        analysis["audio"] = {
            "codec": audio_stream.get("codec_name"),
            "sample_rate": audio_stream.get("sample_rate"),
            "channels": audio_stream.get("channels"),
            "bitrate": audio_stream.get("bit_rate"),
        }

    # Extract audio and analyze beats
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_wav = tmp.name

    try:
        if extract_audio(input_file, tmp_wav):
            beat_info = analyze_beats_simple(tmp_wav)
            analysis["beat_analysis"] = beat_info

            # Generate waveform
            waveform_path = os.path.join(output_dir, "waveform.png")
            if generate_waveform(tmp_wav, waveform_path):
                analysis["waveform_image"] = waveform_path
                print(f"Waveform saved: {waveform_path}")
    finally:
        if os.path.exists(tmp_wav):
            os.unlink(tmp_wav)

    # Save analysis
    analysis_path = os.path.join(output_dir, "analysis.json")
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"Analysis saved: {analysis_path}")
    print(json.dumps(analysis, indent=2))


if __name__ == "__main__":
    main()
