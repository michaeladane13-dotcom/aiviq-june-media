---
description: Iterate text through humanize -> ai-check until the AI-detection score drops below threshold
argument-hint: [text to humanize, or a file path] (optional --target N, default 6)
---

# Humanize Pass — closed-loop humanizer

You are running a closed humanize → score → re-humanize loop. This is the free local
equivalent of a paid humanizer: the `humanize` skill is the rewrite engine, the `ai-check`
skill is the detector, and you drive them against each other until the score drops.

## Input

The text to work on is below. If it's a file path, read the file first.

<input>
$ARGUMENTS
</input>

If no text was provided, ask the user to paste it and stop.

## Target

Default target score is **6 / 27** (top of the "Likely Human" band). If the input contains
`--target N`, use N instead. Strip the `--target N` token out of the text before processing.

## Loop (max 3 iterations)

1. **Humanize.** Invoke the `humanize` skill on the current text. Preserve meaning, structure,
   register, and any signature/voice. Do not invent facts — if the text is a personal/specific
   piece, surface real domain detail rather than fabricating names or events.
2. **Score.** Invoke the `ai-check` skill on the humanized output. Capture the overall score
   and the per-signal breakdown.
3. **Decide.**
   - If overall score <= target → stop, you're done.
   - If 3 iterations reached → stop, report the best version you have.
   - Otherwise → re-run step 1, but this time aim the rewrite **specifically at the signals
     that scored highest** in step 2. Tell the humanize pass which signals fired (e.g. "Signal I
     rhetorical scaffolding = 2: kill the mini-aphorism closer and the parallel-subject mirror";
     "Signal E specificity = 3: anchor with real detail"). Feed it the exact quotes ai-check flagged.

## Hard ceiling — be honest

`ai-check` is rules-based. Real learned classifiers (Pangram, GPTZero) are tougher, and the
one signal no rewrite can fix is **specificity (Signal E)** when the content itself is generic
and names no real people, dates, numbers, or events. If Signal E stays high after iteration 1
because the source has zero real anchors, STOP looping and tell the user plainly: the content,
not the wording, is the tell. Offer the two real fixes — add genuine specifics, or supply a
sample of the target author's real writing so the voice can be matched.

## Output

Output, in this order:
1. The final humanized text only (no preamble around it).
2. A one-line score trail showing the drop, e.g. `Score: 13 -> 7 -> 5 / 27 (Likely Human)`.
3. If any signal is still >= 2, one line naming what's left and the cheapest fix.
