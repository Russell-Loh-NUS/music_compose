from note_seq import (
    MelodyInferenceError,
    MusicXMLConversionError,
    musicxml_file_to_sequence_proto,
    note_sequence_to_midi_file,
    midi_file_to_sequence_proto,
    melody_inference,
)
from note_seq import sequences_lib
import note_seq
import argparse
import glob
from pathlib import Path
from uuid import uuid4

CHORD_SYMBOL = note_seq.NoteSequence.TextAnnotation.CHORD_SYMBOL


def process_musicxml_and_infer_chords(input_filename, output_dir: str):
    """
    Processes a MusicXML file, splits it by measure, quantizes, and infers chords.

    Args:
        input_filename: Path to the input MusicXML file.
    """

    # infer via filename
    if input_filename.endswith("mxl"):
        try:
            ns = musicxml_file_to_sequence_proto(input_filename)
        except MusicXMLConversionError as e:
            print(f"Error Processing: {e}")
            return
    elif input_filename.endswith("mid"):
        ns = midi_file_to_sequence_proto(input_filename)
    else:
        raise FileNotFoundError("Please rename file with either .mxl or .mid")

    # Normalize all to 120 beats per minute
    # sequences_lib.adjust_notesequence_times(ns, 120)

    # Transpose all to C major
    # c_major_key = 0  # C major has key number 0
    # ns = sequences_lib.transpose_note_sequence(
    #    ns, c_major_key - ns.key_signatures[0].key
    # )

    # Split note_seq at every measure
    split_sequences = sequences_lib.split_note_sequence_on_time_changes(ns)


    ## infer melody from chord
    for seq in split_sequences:
        try:
            melody_instrument = melody_inference.infer_melody_for_sequence(
                seq,
            )
        except MelodyInferenceError as e:
            print("No Melody Inference.")
            print(e)
            continue
        # Remove non-melody notes from score.
        score_notes = []
        for note in seq.notes:
            if note.instrument == melody_instrument:
                score_notes.append(note)
        del seq.notes[:]
        seq.notes.extend(score_notes)

    output = []
    ## Process the chorded sequences
    for i, chorded_seq in enumerate(split_sequences):
        try:
            path = Path(output_dir)
            fp = path
            fp.mkdir(exist_ok=True)
            note_sequence_to_midi_file(
                chorded_seq, output_file=(fp / (uuid4().hex + ".mid"))
            )
        except IndexError:
            print(f"No Inference at sequence: {i}")
            continue
        note_list = []
        beat_start_list = []
        beat_end_list = []
        for note in chorded_seq.notes:
            note_list.append(note.pitch)
            beat_start_list.append(note.start_time)
            beat_end_list.append(note.end_time)

    note_seq.musicxml_file_to_sequence_proto
    return output


if __name__ == "__main__":
    ## Inputs
    parser = argparse.ArgumentParser(
        description="Process input file and save to output directory"
    )
    parser.add_argument("-o", "--output", required=False, help="Output directory")
    args = parser.parse_args()

    path = Path(args.output)

    path.mkdir(exist_ok=True)
    ## Process
    mid_files = glob.glob("../../../Downloads/archive/giantmidi-piano-unzipped-midi-v1.21-clean/*.mid")

    for p in mid_files:
        try:
            output = process_musicxml_and_infer_chords(p, path.absolute().as_posix())
        except:
            print(p)
