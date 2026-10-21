import unittest
from types import SimpleNamespace
from lesson_timing import sentence_units, captions_from_words, cue_events, apply_progressive_reveal

def transcript(words):
    return {"segments": [{"start": 0, "end": 20, "text": "", "words": words}]}

class TimingTests(unittest.TestCase):
    def test_pauses_preserve_source_timestamps(self):
        tr = transcript([dict(word="Entry.", start=1, end=2), dict(word=" Release.", start=10, end=12)])
        captions = captions_from_words(sentence_units(tr, 15, str.strip), 15, str.strip, lambda _: False)
        self.assertEqual([(c['start'], c['end']) for c in captions], [(1, 2), (10, 12)])

    def test_decimal_token_and_cleanup_keep_timing(self):
        tr = transcript([dict(word=" calv", start=.5, end=1), dict(word=" 1.3", start=1, end=2), dict(word=" opens.", start=2, end=4)])
        clean = lambda s: s.strip().replace('calv 1.3', 'CaV1.3')
        units = sentence_units(tr, 3.8, clean)
        self.assertEqual(len(units), 1)
        self.assertEqual(captions_from_words(units, 3.8, clean, lambda _: False), [dict(start=.5, end=3.8, text='CaV1.3 opens.')])

    def test_segment_overlap_is_clamped(self):
        tr = {'segments': [dict(start=-1, end=4, text='First.'), dict(start=3, end=8, text='Second.')]}
        result = captions_from_words(sentence_units(tr, 6, str.strip), 6, str.strip, lambda _: False)
        self.assertEqual([(c['start'], c['end']) for c in result], [(0, 4), (4, 6)])

    def test_focus_tracks_sentence_and_reveal(self):
        diagram = SimpleNamespace(shapes=[dict(id='entry'), dict(id='release')], groups={'entry': ['entry'], 'release': ['release', 'missing']}, progressive=['release'])
        units = [dict(start=0, end=3, text='Entry.'), dict(start=12, end=16, text='Release follows.')]
        cues = cue_events(diagram, units, 20, 'Entry title')
        self.assertEqual(next(c for c in cues if c['start'] == 12)['focus'], ['release'])
        apply_progressive_reveal(diagram, cues)
        self.assertEqual(diagram.shapes[1]['introducedAt'], 12)
        self.assertTrue(all(0 <= c['start'] < c['end'] <= 20 for c in cues))

    def test_empty_transcript(self):
        units = sentence_units({'segments': []}, 5, str.strip)
        self.assertEqual(captions_from_words(units, 5, str.strip, lambda _: False), [])
        self.assertEqual(cue_events(SimpleNamespace(shapes=[], groups={}), units, 5, ''), [])

    def test_invalid_duration(self):
        for duration in (0, -1, float('nan'), float('inf')):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                sentence_units({'segments': []}, duration, str.strip)

    def test_filter_removes_unwanted_text(self):
        units = sentence_units({'segments': [dict(start=0, end=1, text='Ignore.')]}, 2, str.strip)
        self.assertEqual(captions_from_words(units, 2, str.strip, lambda _: True), [])

if __name__ == '__main__':
    unittest.main()
