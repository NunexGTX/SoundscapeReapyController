#!/bin/bash

#This conversion script was generated with an LLM provided by Anthropic's Claude Code

# convert_wav_48k.sh
# Recursively finds all .wav files in subdirectories and converts
# any that aren't 48000Hz to 48000Hz, replacing the original.

TARGET_RATE=48000
CONVERTED=0
SKIPPED=0
FAILED=0

find . -type f -iname "*.wav" | while IFS= read -r wav; do
    # Get current sample rate
    current_rate=$(ffprobe -v error -select_streams a:0 \
        -show_entries stream=sample_rate \
        -of default=noprint_wrappers=1:nokey=1 "$wav" 2>/dev/null)

    if [ -z "$current_rate" ]; then
        echo "[SKIP]  Could not read: $wav"
        FAILED=$((FAILED + 1))
        continue
    fi

    if [ "$current_rate" -eq "$TARGET_RATE" ]; then
        echo "[OK]    $wav ($current_rate Hz)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    echo "[CONV]  $wav ($current_rate Hz → $TARGET_RATE Hz)"

    tmp="${wav}.tmp_$$.wav"

    if ffmpeg -y -i "$wav" -ar "$TARGET_RATE" "$tmp" -loglevel error; then
        mv "$tmp" "$wav"
        echo "        ✓ Replaced."
        CONVERTED=$((CONVERTED + 1))
    else
        echo "        ✗ Conversion failed, original kept."
        rm -f "$tmp"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "Done. Converted: $CONVERTED | Already 48kHz: $SKIPPED | Failed: $FAILED"