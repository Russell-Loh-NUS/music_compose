import mido

class CreateMidi:
    def create_midi_from_notes(output_file, notes, ticks_per_beat=480, tempo=500000): #ticks per beat and tempo controls the overall pace of the song i.e how fast or slow the song will be.
        midi = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        track = mido.MidiTrack() # Create single track
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        midi.tracks.append(track)

        # Sort notes so that its in order of the start time
        notes = sorted(notes, key=lambda x: x['start_time'])
        for note_data in notes:
            note = note_data['note'] # The note in the range of 0-127 indicating its Pitch.
            start_time = note_data['start_time'] # Starting time of note
            duration = note_data['duration'] # How long note is held
            velocity = note_data.get('velocity', 64)  # Velocity of the note is how HARD the note is stuck i.e Loudness. Set default to 64.

            # Calculate time offset for the note_on event
            if(note_data['event'] == 'note_on'):
                track.append(mido.Message('note_on', note=note, velocity=velocity, time=0))
            
            if(note_data['event'] == 'note_off'):
                # Add note_off event after the duration
                track.append(mido.Message('note_off', note=note, velocity=0, time=duration))

        # Save the MIDI file
        midi.save(output_file)
        print(f"MIDI file '{output_file}' created. Please find it in the root folder.")