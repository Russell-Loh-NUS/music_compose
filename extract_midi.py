import sys
import mido

class ExtractMidi:
    def extract_midi_data(file_path):
        midi = mido.MidiFile(file_path) # Load the MIDI file
        ticks_per_beat = midi.ticks_per_beat # Important for reconstructing back the midi
        print('Ticks per beat: ' + str(ticks_per_beat))
        notes = {}
        midi_data = []
        tempo = sys.maxsize # Default tempo is 500000 microseconds
        tempo_list = [] # Store all tempo messages

        count = 0
        for track in midi.tracks: # Loop through each track
            print("Track: " + str(count))
            time_in_ticks = 0
            count += 1
            for message in track:
                time_in_ticks += message.time  # Update cumulative time in ticks

                if message.type == 'set_tempo':
                    tempo_list.append({
                        'tempo': message.tempo,
                        'time': message.time
                    })
                if message.type == 'set_tempo' and message.tempo < tempo: # For now, we get the lowest tempo among all the tempo set. Potentially we should recalculate the duration using the tempo set (?)
                    tempo = message.tempo
                    print("Tempo:" + str(tempo) + ", Time: " + str(message.time))

                if message.type == 'note_on' and message.velocity > 0:  # Note start
                    notes[message.note] = {
                        'start_time': time_in_ticks,
                        'velocity': message.velocity
                    }

                    # Add the note_on event to the midi_data
                    midi_data.append({
                        'event': 'note_on',
                        'note': message.note,
                        'velocity': message.velocity,
                        'start_time': time_in_ticks,
                        'duration': None,
                    })

                elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):  # Note end
                    if message.note in notes:
                        # Calculate duration in ticks
                        start_time = notes[message.note]['start_time']

                        # Add the note_off event to the midi_data
                        midi_data.append({
                            'event': 'note_off',
                            'note': message.note,
                            'velocity': message.velocity,
                            'start_time': start_time,
                            'duration': message.time
                        })

        return ticks_per_beat, tempo, tempo_list, midi_data