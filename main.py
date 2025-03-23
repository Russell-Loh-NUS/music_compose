from extract_midi import ExtractMidi
from create_midi import CreateMidi

def process_midi(file_path):
    ticks_per_beat, tempo, notes = ExtractMidi.extract_midi_data(file_path) # Extract the midi data. The notes will be in order of start time.

    note_transitions_count = {} # N x N matrix of the count of note transitions. Row = From Note, Column = To Note
    note_duration = {} # Returns note: (total_duration, total_note_count). The total duration of each note assuming duration is independent.
    total_notes = 0
    output_notes = []

    # Loop through all notes
    prev_note = None
    for note in notes:
        # print(f"Event: {note['event']}, Note: {note['note']}, Velocity: {note['velocity']}, "
        #     f"Start Time: {note['start_time']} ticks, Duration: {note['duration']} ticks)")
        
        output_notes.append({'event': note['event'], 'note': note['note'], 'start_time': note['start_time'], 'duration': note['duration'], 'velocity': note['velocity']})
        
        # We only process the note offs as every note has an on/off pair.
        # Plus, only the off notes contain the duration.
        if note['event'] == 'note_on':
            continue

        # Populate the note transitions count
        if prev_note != None:
            if prev_note['note'] not in note_transitions_count: # Check and add previous note if it was not added yet
                note_transitions_count[prev_note['note']] = {}
            if note['note'] not in note_transitions_count[prev_note['note']]: # Check and add current note if it was not added yet
                note_transitions_count[prev_note['note']][note['note']] = 0
            note_transitions_count[prev_note['note']][note['note']] += 1 # Increment count
        
        # Populate the note duration avg
        if note['note'] not in note_duration:
            note_duration[note['note']] = [0, 0] # [0] - total_duration, [1] - total note count
        note_duration[note['note']][0] += note['duration'] or 0 # Increment total_duration
        note_duration[note['note']][1] += 1 # Increment note count
            
        prev_note = note # Set current note to be previous note
        total_notes += 1
    
    return ticks_per_beat, tempo, total_notes, output_notes, note_transitions_count, note_duration

# Process MIDI
input_path = 'midi_files/1.mid' # Change this to the file path accordingly
ticks_per_beat, tempo, total_notes, output_notes, note_transitions_count, note_duration = process_midi(input_path)

print()
print('.:PROCESSING MIDI:.')
print('Total On/Off Notes Pair: ' + str(total_notes))
print('Note Transitions Count - Row = From Note, Column = To Note')
print(note_transitions_count)

print('Note Duration - note: (total duration, note count)')
print(note_duration)

# Create MIDI file from notes
print()
print('.:CREATING MIDI:.')
output_file_path = 'output.mid'
print("Ticks per beat: " + str(ticks_per_beat) + ", Tempo: " + str(tempo))
CreateMidi.create_midi_from_notes(output_file_path, output_notes, ticks_per_beat, tempo)