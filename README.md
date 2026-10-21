# MediByte Lesson Timing

Small Python tools for turning timestamped transcripts into captions and narration linked diagram cues. Extracted from the MediByte medical education project by Roham Aksoy, a physician and software developer, with Codex assistance.

## Why this exists

A diagram should follow the explanation. Dividing a recording into equal intervals loses pauses and can highlight the wrong structure while the teacher is speaking. These tools retain source word timestamps, group captions into readable chunks, and match spoken terms to diagram shape IDs.

This is a newly published component, with no claim of broad adoption. It is not the complete MediByte application or a medical curriculum.

## Run

Python 3.10 or newer; standard library only. No account, API key, audio download or network access is needed.

```sh
python3 demo.py
python3 -m unittest discover -s . -v
```

The demo prints captions, highlight intervals and progressive shape introduction times for a synthetic example. It does not play audio or draw a board.

## API

* `sentence_units(transcript, duration, clean)` groups source words at sentence boundaries.
* `captions_from_words(units, duration, clean, is_trash)` creates readable caption intervals.
* `cue_events(diagram, units, duration, title)` matches text against diagram groups.
* `apply_progressive_reveal(diagram, cues)` annotates selected shapes with `introducedAt`.

Times are seconds. `duration` must be finite and positive. Word tokens must retain their leading spaces, as in common ASR exports. Each transcript has a `segments` list; each segment has `start`, `end`, `text` and optional `words`. Each word has `word`, `start`, `end`. Inputs are expected in chronological order with finite numeric timestamps. Empty transcripts produce no captions or cues.

A diagram exposes `shapes` (dictionaries with unique `id` values), `groups` (term strings mapped to shape ID lists), and optional `progressive` (shape IDs to introduce over time). See `demo.py` for the complete contract.

`clean` changes transcription text without moving word timestamps. Do not use it to conceal incorrect spoken teaching. `is_trash` is an application supplied filter. Progressive reveal mutates the diagram's shape dictionaries.

## Limitations

Cue matching is a deterministic keyword heuristic, not semantic understanding. It does not understand negation. Sparse matches produce fallback scaffold cues around one third and two thirds of the recording; the initial cue is moved to time zero. Those cues are not evidence that a term was spoken at that time. Review generated timelines before publication. Closely spaced or identical focus changes are suppressed for readability.

The tools do not transcribe audio, validate medical claims, provide diagnosis, or replace editorial review. Fixtures are synthetic timing examples, not clinical guidance. Malformed ASR exports need normalization upstream. Caption cleanup cannot repair factual errors in a recording.

## Provenance and scope

The initial algorithm comes from MediByte's `physiology_timing.py`. This standalone extraction adds duration validation, empty transcript handling, bounded nonoverlapping segment captions and pause safe scaffold selection. Tests are adapted from its original timing regression cases and extended for standalone use. The original application has not been modified by this extraction.

Only the timing code, synthetic examples, documentation and tests are included. Application media, voice recordings, learner information, credentials, backend configuration and the original Git history are not part of this repository.

## Contributing

Useful contributions include synthetic regression cases for pauses, punctuation, overlapping timestamps and cue matching. Run the test command above and describe the observed behavior. Do not submit patient data, private recordings, credentials or copyrighted course material. This project currently has one maintainer and no response time guarantee.

## License

MIT. See `LICENSE`.
