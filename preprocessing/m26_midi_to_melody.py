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
    if input_filename.endswith("mid"):
        melody = note_seq.midi_file_to_melody(input_filename)
        ns = melody.to_sequence()
    else:
        raise FileNotFoundError("Please rename file .mid")

    ## write to file
    path = Path(output_dir)
    fp = path
    fp.mkdir(exist_ok=True)
    name = input_filename.rsplit('/')[-1]
    note_sequence_to_midi_file(
        ns, output_file=(fp / ("cleaned_"+ name))
    )

    return None


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
    mid_files = glob.glob("./input_directory/*.mid")

    for p in mid_files:
        try:
            output = process_musicxml_and_infer_chords(p, path.absolute().as_posix())
        except:
            pass
