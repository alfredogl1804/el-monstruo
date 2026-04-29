---
name: tiktok-trend-creator
description: Create viral TikTok trend concepts and seed videos from music video clips. Use for generating trend ideas from songs, designing replicable couple/humor video concepts synced to music, analyzing songs for viral potential, scripting seed videos, and producing edited TikTok-ready videos with text overlays. Focused on couples and humor niches.
---

# TikTok Trend Creator

Create viral TikTok trend concepts and seed videos from music clips. Focused on **couples** and **humor** niches.

## Workflow

Creating a TikTok trend from a music clip involves these steps:

1. **Receive and analyze** the music video/audio
2. **Identify viral moments** in the song (or use the user-specified fragment)
3. **Design the trend concept** (idea, archetype, script)
4. **Produce the seed video** (edit video with text overlays)
5. **Deliver** concept document + edited video

## Step 1: Receive and Analyze the Song

When the user provides a video/audio file, run the analysis script:

```bash
python3 scripts/analyze_song.py <input_file> <output_dir>
```

This produces `analysis.json` (duration, beat timestamps, audio properties) and `waveform.png`.

Additionally, transcribe the lyrics using `manus-speech-to-text`:

```bash
manus-speech-to-text <input_file>
```

Review the transcription to understand the song's lyrics, mood, and theme.

## Step 2: Identify Viral Moments

Analyze the song to find the most "TikTok-able" fragments (15-30 seconds). Look for:

- **Catchy hooks or choruses** with repetitive, memorable phrases
- **Beat drops** where energy shifts dramatically
- **Emotional peaks** (lyric climax, vocal intensity change)
- **Funny or quotable lines** that can be taken out of context
- **Silence-to-loud transitions** that create natural punchline moments

If the user specifies a fragment, use that. Otherwise, propose 2-3 candidate fragments with timestamps and reasoning.

Extract the chosen fragment:

```bash
python3 scripts/extract_clip.py <input_file> <start> <end> <output_clip> --tiktok
```

## Step 3: Design the Trend Concept

Read `references/trend_formulas.md` for trend archetypes and virality principles.

Select the best archetype for the song fragment. The seven archetypes are:

| Archetype | Best when the fragment has... |
|-----------|-------------------------------|
| Reaction Reveal | A surprising beat drop or lyric twist |
| Relatable Confession | Lyrics about everyday situations |
| Before/After Transition | A clear energy shift or tempo change |
| Challenge/Dare | Lyrics that imply a question or dare |
| Duet Bait | A call-and-response structure |
| Lip-Sync Skit | Dialogue-like lyrics or spoken word |
| Unexpected Twist | A beat switch or ironic lyric |

Create the concept using the template at `templates/trend_concept.md`. Fill in every section:

- **Idea**: 2-3 sentences anyone can understand
- **Guion**: Second-by-second script synced with the music (use a table)
- **Hook**: What captures attention in the first 3 seconds
- **Variaciones**: At least 3 ways others can adapt it
- **Replicability**: Must pass ALL items in the replicability checklist (see `references/trend_formulas.md` section 5)

For hashtags and captions, consult `references/hashtag_strategy.md`.

## Step 4: Produce the Seed Video

Create a JSON config file based on `templates/seed_video_config.json`:

```json
{
  "input_file": "clip.mp4",
  "background_color": "black",
  "width": 1080,
  "height": 1920,
  "texts": [
    {
      "text": "POV: Your text here",
      "start": 0.0,
      "end": 3.0,
      "position": "top",
      "fontsize": 60,
      "color": "white"
    }
  ]
}
```

Position options: `top`, `center_top`, `center`, `center_bottom`, `bottom`.

Run the video creation script:

```bash
python3 scripts/create_seed_video.py <config.json> <output.mp4>
```

The script handles both video and audio-only inputs. For audio-only files, it generates a colored background with text overlays.

## Step 5: Deliver

Deliver to the user:

1. **Trend concept document** (filled template from step 3) as a Markdown file
2. **Seed video** (.mp4) ready for TikTok upload
3. **Brief summary** explaining the concept and why it has viral potential

## Key Guidelines

- Every concept MUST be designed for the **couples + humor** niche
- The trend MUST be replicable by anyone with just a phone in under 5 minutes
- Text overlays should be in **Spanish** by default (add English if user requests bilingual)
- Always propose the trend concept BEFORE producing the video, so the user can approve or adjust
- If the user only wants the concept (no video editing), skip step 4
- Video format: vertical 9:16 (1080x1920), 30fps, max 60 seconds
