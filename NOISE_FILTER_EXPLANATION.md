# Noise Filter Explanation - How It Filters Keyboard Clicks

## Overview

The noise filter prevents the voice activation system from triggering on mechanical keyboard sounds, mouse clicks, and other environmental noise. It uses multiple audio analysis techniques to distinguish between **speech** and **noise**.

## How It Works - Step by Step

### Step 1: Audio Analysis

When audio comes in, the filter analyzes these characteristics:

1. **Duration** - How long the sound lasts
2. **Energy** - How loud the sound is
3. **Zero-Crossing Rate (ZCR)** - How "sharp" the waveform is
4. **Frequency Content** - What frequencies are present
5. **Spectral Centroid** - How "bright" the sound is
6. **Attack Sharpness** - How suddenly the sound starts

### Step 2: Comparison with Known Patterns

The filter compares the audio against known patterns:

**Mechanical Keyboard Click:**
- Duration: ~15-30ms (very short)
- Energy: High (0.01-0.05) - loud click
- ZCR: Very high (0.5-0.7) - sharp transient
- High frequency: 40-60% - lots of high frequencies
- Spectral centroid: 3000-5000Hz - very bright
- Attack: Very sharp (0.4-0.6) - instant onset

**Human Speech:**
- Duration: 100-500ms+ (sustained)
- Energy: Moderate (0.001-0.01) - sustained but lower peak
- ZCR: Lower (0.2-0.3) - smoother waveform
- High frequency: 10-20% - mostly low/mid frequencies
- Spectral centroid: 1000-2000Hz - warmer sound
- Attack: Gradual (0.1-0.2) - smooth onset

### Step 3: Scoring System

The filter uses a scoring system:

- **Score 0-4**: Likely speech → PASS
- **Score 5-7**: Possibly a click → FILTER
- **Score 8+**: Definitely a click → FILTER

Each characteristic adds points:
- Very short duration (<20ms): +5 points
- High energy: +2-3 points
- High ZCR: +2-3 points
- High frequency content: +2-3 points
- Sharp attack: +2 points
- Sharp transient: +3 points

## Real-World Examples

### Example 1: Mechanical Keyboard Press

**Audio Signal:**
```
Time: 0ms ────────────────────────── 15ms
Amplitude: [silence] → [LOUD CLICK] → [silence]
```

**Analysis:**
- Duration: 15ms ✅ (very short)
- Energy: 0.025 ✅ (high)
- ZCR: 0.65 ✅ (very sharp)
- High freq: 48% ✅ (very clicky)
- Spectral centroid: 3800Hz ✅ (bright)
- Attack: 0.52 ✅ (very sharp)
- Sharp transient: Yes ✅

**Score: 15 points** → **FILTERED** ❌

**Result:** System ignores the keyboard click, does NOT start recording.

---

### Example 2: Human Speech "Hello"

**Audio Signal:**
```
Time: 0ms ────────────────────────────────────────── 400ms
Amplitude: [gradual rise] → [sustained "hello"] → [gradual fall]
```

**Analysis:**
- Duration: 400ms ✅ (sustained)
- Energy: 0.004 ✅ (moderate, sustained)
- ZCR: 0.22 ✅ (smooth)
- High freq: 14% ✅ (mostly low/mid)
- Spectral centroid: 1350Hz ✅ (warm)
- Attack: 0.15 ✅ (gradual)
- Sharp transient: No ✅

**Score: 2 points** → **PASSED** ✅

**Result:** System recognizes speech, starts recording.

---

### Example 3: Rapid Typing (Multiple Clicks)

**Audio Signal:**
```
Time: 0ms ──[click]──[click]──[click]──[click]── 200ms
Amplitude: Multiple short bursts
```

**Analysis:**
- Each click: ~20ms duration
- Pattern: Multiple short bursts
- Each click scores 8-12 points
- Filter detects pattern → **FILTERED** ❌

**Result:** System ignores typing, does NOT start recording.

---

### Example 4: Speech with Background Typing

**Audio Signal:**
```
Time: 0ms ────────────────────────────────────────── 500ms
Amplitude: [speech "hello"] + [faint keyboard clicks in background]
```

**Analysis:**
- Main signal: Speech characteristics (400ms, smooth, low freq)
- Background: Faint clicks (filtered out)
- Overall: Speech pattern dominates

**Score: 3 points** → **PASSED** ✅

**Result:** System recognizes speech over background noise, starts recording.

---

## Multi-Layer Protection

The system has **three layers** of protection:

### Layer 1: Noise Filter
- Analyzes audio characteristics
- Filters out obvious clicks
- **Example:** Mechanical keyboard click → Filtered immediately

### Layer 2: Sustained Speech Requirement
- Requires 5 consecutive frames (100ms) of speech
- Prevents single clicks that slip through
- **Example:** Even if one frame passes, need 4 more → Prevents false trigger

### Layer 3: WebRTC VAD
- Confirms it's actual speech
- Industry-standard voice activity detection
- **Example:** Final confirmation that it's human speech

## Configuration

You can adjust sensitivity in `config.yaml`:

```yaml
voice_activation:
  sensitivity: 0.5  # Lower = less sensitive (filters more)
```

The noise filter automatically adjusts thresholds based on:
- Audio duration
- Energy levels
- Frequency patterns

## Troubleshooting

**Problem:** System triggers on keyboard
- **Solution:** The filter should catch this. Check logs for "Detected click" messages
- If still happening, increase `min_speech_frames` in code

**Problem:** System doesn't trigger on speech
- **Solution:** Check if noise filter is too aggressive
- Look for "Ignoring click/noise sound" in logs when you speak
- May need to adjust thresholds

**Problem:** Empty transcriptions
- **Solution:** Check audio energy in logs
- Very low energy (< 1e-6) = microphone not picking up sound
- Normal energy but empty = Whisper model issue

## Technical Details

### Zero-Crossing Rate (ZCR)
- Measures how often the waveform crosses zero
- Clicks: High ZCR (0.5-0.7) = sharp, jagged waveform
- Speech: Low ZCR (0.2-0.3) = smooth, rounded waveform

### Spectral Centroid
- Average frequency weighted by energy
- Clicks: High (3000-5000Hz) = bright, sharp sound
- Speech: Lower (1000-2000Hz) = warmer, fuller sound

### Attack Sharpness
- How quickly sound reaches peak energy
- Clicks: Very sharp (0.4-0.6) = instant onset
- Speech: Gradual (0.1-0.2) = smooth rise

## Summary

The noise filter uses **multiple audio characteristics** to create a **scoring system** that distinguishes:
- ✅ **Speech** (sustained, smooth, lower frequencies) → PASS
- ❌ **Keyboard clicks** (short, sharp, high frequencies) → FILTER
- ❌ **Mouse clicks** (similar to keyboard) → FILTER
- ❌ **Environmental noise** (various patterns) → FILTER

This ensures the system only triggers on **actual human speech**, not on typing or other environmental sounds.

