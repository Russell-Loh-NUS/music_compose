import os
import numpy as np
import pretty_midi

def get_midi_duration(midi_path):
    """Returns duration of a MIDI file in seconds."""
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        return midi_data.get_end_time()
    except Exception as e:
        print(f"Error reading {midi_path}: {e}")
        return None

def compute_median_duration(directory):
    """Computes median duration of all MIDI files in a directory."""
    durations = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.mid', '.midi')):
            filepath = os.path.join(directory, filename)
            duration = get_midi_duration(filepath)
            if duration is not None:
                durations.append(duration)
    return np.median(durations) if durations else None

def cut_midi_to_duration(input_path, output_path, target_duration):
    """Cuts a MIDI file to the specified duration (or loops if shorter)."""
    midi_data = pretty_midi.PrettyMIDI(input_path)
    original_duration = midi_data.get_end_time()
    
    if original_duration >= target_duration:
        # Trim the MIDI (remove events after target_duration)
        for instrument in midi_data.instruments:
            instrument.notes = [note for note in instrument.notes if note.start < target_duration]
    else:
        # Loop the MIDI (repeat notes until target_duration is reached)
        loop_times = int(np.ceil(target_duration / original_duration))
        for instrument in midi_data.instruments:
            new_notes = []
            for loop in range(loop_times):
                for note in instrument.notes:
                    new_note = pretty_midi.Note(
                        velocity=note.velocity,
                        pitch=note.pitch,
                        start=note.start + loop * original_duration,
                        end=note.end + loop * original_duration
                    )
                    if new_note.start < target_duration:
                        new_notes.append(new_note)
            instrument.notes = new_notes
    
    midi_data.write(output_path)

def process_all_midis(input_dir, output_dir):
    """Processes all MIDI files to the median duration."""
    median_duration = compute_median_duration(input_dir)
    if median_duration is None:
        print("No valid MIDI files found.")
        return
    
    print(f"Median duration: {median_duration:.2f} seconds")
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.mid', '.midi')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            cut_midi_to_duration(input_path, output_path, median_duration)
            print(f"Processed: {filename}")

# Example usage:
input_directory = "./input_directory"
output_directory = "./output_directory"
process_all_midis(input_directory, output_directory)
