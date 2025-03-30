from note_seq import (
    chord_inference,
    musicxml_file_to_sequence_proto,
    note_sequence_to_midi_file,
    midi_file_to_sequence_proto,
)
from note_seq import sequences_lib
import note_seq
import json
import os
import sys
import argparse
from pathlib import Path
from uuid import uuid4

CHORD_SYMBOL = note_seq.NoteSequence.TextAnnotation.CHORD_SYMBOL


def process_musicxml_and_infer_chords(input_filename, output_dir=None):
    """
    Processes a MusicXML file, splits it by measure, quantizes, and infers chords.

    Args:
        input_filename: Path to the input MusicXML file.
    """

    # infer via filename
    if input_filename.endswith("mxl"):
        ns = musicxml_file_to_sequence_proto(input_filename)
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
    split_sequence_tmp = sequences_lib.split_note_sequence_on_time_changes(ns)
    split_sequences = []

    for split_sequence in split_sequence_tmp:
        # Get QPM and time signature for the current split
        qpm = split_sequence.tempos[0].qpm
        time_signature = split_sequence.time_signatures[0]

        # Calculate the duration of one measure in seconds
        hop_size = (time_signature.numerator * 60 * 4) / (
            time_signature.denominator * qpm
        )

        split_sequences.extend(
            sequences_lib.split_note_sequence(split_sequence, hop_size)
        )

    # Quantize each split
    quantized_sequences = []
    for seq in split_sequences:
        try:
            # quantized_seq = sequences_lib.quantize_note_sequence_absolute(
            #    seq, int(seq.total_time))
            quantized_seq = sequences_lib.quantize_note_sequence(
                seq, steps_per_quarter=4
            )  # or any other steps_per_quarter
            quantized_sequences.append(quantized_seq)
        except sequences_lib.QuantizationStatusError as e:
            print(f"Quantization error: {e}")
            continue

    ## Chord inference for all sequences
    ## Ignore 0 chord inference, loss incurred
    for quantized_seq in quantized_sequences:
        try:
            chord_inference.infer_chords_for_sequence(quantized_seq)
        except chord_inference.EmptySequenceError as e:
            print(f"EmptySequence error: {e}")
            continue
        except chord_inference.UncommonTimeSignatureError as e:
            print(f"UncommonTimeSignatureError: {e}")
            continue

    ## Join if chords are the same
    concatenated_sequences = []
    cur_seq = []
    cur_chord = None
    for seq in quantized_sequences:
        # unquantized_note_sequence
        # Not different chords
        ## hack
        seq.quantization_info.steps_per_quarter = 0

        if (
            not seq.text_annotations
            or seq.text_annotations[0].annotation_type != CHORD_SYMBOL
        ):
            cur_seq.append(seq)
            continue
        if cur_chord is None:
            cur_chord = seq.text_annotations[0].text
            cur_seq.append(seq)
        elif cur_chord == seq.text_annotations[0].text:
            cur_seq.append(seq)
        else:
            cur_chord = seq.text_annotations[0].text
            concatenated_sequences.append(sequences_lib.concatenate_sequences(cur_seq))
            cur_seq = [seq]
        print(
            f"Concatenating chord: {seq.text_annotations[0].text} , current sequence length: {len(cur_seq)}"
        )

    output = []
    ## Process the chorded sequences
    for i, chorded_seq in enumerate(concatenated_sequences):
        try:
            if chorded_seq.text_annotations[0].annotation_type == CHORD_SYMBOL:
                seg = {"CHORD_SYMBOL": chorded_seq.text_annotations[0].text}
                if output_dir:
                    path = Path(output_dir)
                    note_sequence_to_midi_file(
                        chorded_seq, output_file=(path / (str(i) + ".mid"))
                    )
            else:
                print(f"Invalid text annotation for sequence: {i}")
                continue
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
        seg.update(
            {
                "notes": note_list,
                "beat_starts": beat_start_list,
                "beat_ends": beat_end_list,
            }
        )
        output.append(seg)

    note_seq.musicxml_file_to_sequence_proto
    return output


if __name__ == "__main__":
    ## Inputs
    parser = argparse.ArgumentParser(
        description="Process input file and save to output directory"
    )
    parser.add_argument("-i", "--input_file", required=True, help="Input filename")
    parser.add_argument("-o", "--output", required=False, help="Output directory")
    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_file):
        sys.exit(f"Error: Input file '{args.input_file}' does not exist")
    if not os.path.isfile(args.input_file):
        sys.exit(f"Error: '{args.input_file}' is not a regular file")

    ## Artifact directory
    output_dir = uuid4().hex
    if args.output is not None:
        path = Path(args.output) / output_dir
    else:
        path = Path(output_dir)

    path.mkdir(exist_ok=True)

    ## Process
    output = process_musicxml_and_infer_chords(args.input_file, path.absolute())
    output_json = path / "output.json"
    open(output_json, "w").write(json.dumps(output))
    print(f"Completed processing of {args.input_file}")
    print(f"Split midi files created at {path.absolute()}")
