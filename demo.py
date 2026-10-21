"""Run a synthetic two sentence example without external services."""
import json
from types import SimpleNamespace
from lesson_timing import sentence_units, captions_from_words, cue_events, apply_progressive_reveal

transcript = {"segments": [{"start": 0, "end": 16, "text": "Entry begins. Release follows.", "words": [
    {"word": "Entry", "start": 1, "end": 1.5},
    {"word": " begins.", "start": 1.5, "end": 2},
    {"word": " Release", "start": 12, "end": 12.5},
    {"word": " follows.", "start": 12.5, "end": 14},
]}]}
diagram = SimpleNamespace(shapes=[{"id": "entry"}, {"id": "release"}],
    groups={"entry": ["entry"], "release": ["release"]}, progressive=["release"])
units = sentence_units(transcript, 16, str.strip)
captions = captions_from_words(units, 16, str.strip, lambda _: False)
cues = cue_events(diagram, units, 16, "Synthetic timing example")
apply_progressive_reveal(diagram, cues)
print(json.dumps({"captions": captions, "cues": cues, "shapes": diagram.shapes}, indent=2))
