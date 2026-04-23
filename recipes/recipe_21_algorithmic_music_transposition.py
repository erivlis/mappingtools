"""
Recipe 21: Algorithmic Music Transposition (reshape + Lens)

In algorithmic composition or MIDI processing, a song is often represented
as a flat stream of note events. To manipulate the song (like transposing
a specific instrument or extracting a sheet music view), we need to pivot
the flat stream into a structured hierarchy.

This recipe uses `reshape` to group a flat stream of MIDI-like notes into a
timeline (Instrument -> Measure -> Notes). Then, it uses a `Lens` to immutably
transpose the pitch of a specific instrument (the Bass) up an octave, leaving
the rest of the song completely untouched.
"""

from mappingtools.aggregations import Aggregation
from mappingtools.operators import reshape
from mappingtools.optics import Lens


def main():
    # 1. A flat stream of note events (e.g., read from a MIDI file)
    song_events = [
        {"instrument": "Piano", "measure": 1, "pitch": "C4", "duration": "quarter"},
        {"instrument": "Piano", "measure": 1, "pitch": "E4", "duration": "quarter"},
        {"instrument": "Bass",  "measure": 1, "pitch": "C2", "duration": "half"},
        {"instrument": "Piano", "measure": 2, "pitch": "F4", "duration": "half"},
        {"instrument": "Bass",  "measure": 2, "pitch": "F2", "duration": "half"},
    ]

    # 2. Reshape into a Musical Score (Instrument -> Measure -> [Notes])
    # We use Aggregation.ALL to collect the notes into lists for each measure
    score = reshape(
        song_events,
        keys=["instrument", "measure"],
        value=lambda note: {"pitch": note["pitch"], "duration": note["duration"]},
        aggregation=Aggregation.ALL
    )

    print("--- Original Score ---")
    import json
    print(json.dumps(score, indent=2))

    # 3. Define a Transposition Function
    def transpose_octave(notes_list):
        """Transposes a list of notes up by one octave (e.g., C2 -> C3)."""
        transposed = []
        for note in notes_list:
            # A naive pitch transposition (assuming format like "C2")
            note_class = note["pitch"][0]
            octave = int(note["pitch"][1])
            transposed.append({
                **note,
                "pitch": f"{note_class}{octave + 1}"
            })
        return transposed

    # 4. Create an Optic (Lens) that focuses ONLY on the Bass track's first measure
    bass_measure_1_lens = Lens.path("Bass", 1)

    # 5. Immutably modify the song!
    # The Lens dives into the nested score, applies the transposition ONLY to the focused notes,
    # and returns a brand new score object.
    remixed_score = bass_measure_1_lens.modify(score, transpose_octave)

    print("\n--- Remixed Score (Bass Measure 1 Transposed +1 Octave) ---")
    print(json.dumps(remixed_score["Bass"], indent=2))

    print("\n--- Original Score Untouched ---")
    print(json.dumps(score["Bass"], indent=2))


def test_main():
    main()


if __name__ == "__main__":
    main()
