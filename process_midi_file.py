import os
from extract_midi import ExtractMidi
from create_midi import CreateMidi

def process_midi(file_path):
    ticks_per_beat, tempo, tempo_list, notes = ExtractMidi.extract_midi_data(file_path) # Extract the midi data. The notes will be in order of start time.

    pitch_sequence = []  # Sequence of note pitches
    duration_sequence = []  # Sequence of note durations
    total_notes = 0
    
    # Keep all original notes
    output_notes = []
    for note in notes:
        output_notes.append({'event': note['event'], 'note': note['note'], 'start_time': note['start_time'], 
                            'duration': note['duration'], 'velocity': note['velocity']})
    
    # Group notes by start_time and event type
    grouped_notes = {}
    for note in notes:
        key = (note['start_time'], note['event'])
        if key not in grouped_notes:
            grouped_notes[key] = []
        grouped_notes[key].append(note)
    
    # For each group, keep only the highest pitch
    filtered_notes = []
    for group in grouped_notes.values():
        # Find the note with the highest pitch in this group
        highest_note = max(group, key=lambda x: x['note'])
        filtered_notes.append(highest_note)
    
    # Sort by start_time to maintain chronological order
    output_notes_highest = sorted(filtered_notes, key=lambda x: (x['start_time'], x['event'] != 'note_on'))

    # Process the filtered notes to get sequences
    for note in output_notes_highest:
        # We only process the note offs for sequences
        if note['event'] == 'note_on':
            continue
            
        # Collect pitch and duration sequences
        pitch_sequence.append(note['note'])
        duration_sequence.append(note['duration'])
        total_notes += 1
    
    return ticks_per_beat, tempo, total_notes, output_notes, output_notes_highest, pitch_sequence, duration_sequence


if __name__ == "__main__":

    # Process MIDI
    # Change this to the file path accordingly
    input_folder = 'midi_files'
    input_fn = "2.mid"
    input_path = os.path.join(input_folder, input_fn)

    ticks_per_beat, tempo, total_notes, output_notes, output_notes_highest, pitch_sequence, duration_sequence = process_midi(input_path)

    print()
    print('.:PROCESSING MIDI:.')
    print('Total On/Off Notes Pair: ' + str(total_notes))
    print('Pitch Sequence:')
    print(pitch_sequence)
    print('Duration Sequence:')
    print(duration_sequence)

    output_dir = 'sample_outputs'
    # Create another MIDI file from all original notes
    output_fn_all = 'output_all.mid'
    output_path_all = os.path.join(output_dir, input_fn.split(".")[0] + "_" + output_fn_all)
    print("\nCreating MIDI with all original notes")
    CreateMidi.create_midi_from_notes(output_path_all, output_notes, ticks_per_beat, tempo)


    # Create MIDI file from highest notes
    # TODO: ENHANCEMENT: Notice the highest note extracted is not exactly the right most track in the midi file.
    print()
    print('.:CREATING MIDI:.')
    output_fn_highest = 'output_highest.mid'
    output_path_highest = os.path.join(output_dir, input_fn.split(".")[0] + "_" + output_fn_highest)
    print("Creating MIDI with highest notes only")
    print("Ticks per beat: " + str(ticks_per_beat) + ", Tempo: " + str(tempo))
    CreateMidi.create_midi_from_notes(output_path_highest, output_notes_highest, ticks_per_beat, tempo)
