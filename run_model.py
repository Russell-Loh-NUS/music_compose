import os
from process_midi_file import process_midi
from create_midi import CreateMidi
from model.VanillaFirstOrderMarkovChain import VanillaFirstOrderMarkovChain
from model.VanillaSecondOrderMarkovChain import VanillaSecondOrderMarkovChain

input_folder = 'midi_files'
input_fn = "2.mid"  # Change this to the file name accordingly
input_path = os.path.join(input_folder, input_fn)
output_dir = "sample_outputs"

ticks_per_beat, tempo, total_notes, output_notes, output_notes_highest, pitch_sequence, duration_sequence = process_midi(input_path)

# get states
pitch_set = set(pitch_sequence)
duration_set = set(duration_sequence)

# first order
pitch_model_fmc = VanillaFirstOrderMarkovChain(pitch_set)
pitch_model_fmc.calculate_transition_matrix([pitch_sequence])
pitch_pred_seq_fmc = pitch_model_fmc.inference_prob(start_state=None, length=100, random_seed=42)
pitch_model_fmc.visualize_transition_matrix(os.path.join(output_dir, "pitch_transition_matrix_fmc.png"))

duration_model_fmc = VanillaFirstOrderMarkovChain(duration_set)
duration_model_fmc.calculate_transition_matrix([duration_sequence])
duration_pred_seq_fmc = duration_model_fmc.inference_prob(start_state=None, length=100, random_seed=42)
duration_model_fmc.visualize_transition_matrix(os.path.join(output_dir, "duration_transition_matrix_fmc.png"))

# second order
pitch_model_smc = VanillaSecondOrderMarkovChain(pitch_set)
pitch_model_smc.calculate_transition_matrix([pitch_sequence])
pitch_pred_seq_smc = pitch_model_smc.inference_prob(start_state=None, length=100, random_seed=42)
pitch_model_smc.visualize_transition_matrix(os.path.join(output_dir, "pitch_transition_matrix_smc.png"))

duration_model_smc = VanillaSecondOrderMarkovChain(duration_set)
duration_model_smc.calculate_transition_matrix([duration_sequence])
duration_pred_seq_smc = duration_model_smc.inference_prob(start_state=None, length=100, random_seed=42)
duration_model_smc.visualize_transition_matrix(os.path.join(output_dir, "duration_transition_matrix_smc.png"))

# reconstruct midi file
# first order
fmc_output_name = input_fn.split(".")[0] + "_pred_fmc.mid"
fmc_output_path = os.path.join(output_dir, fmc_output_name)
fmc_seq = []
current_time = 0
# TODO: QN: What is the velocity? How to set it?
velocity = 110 # this is the one in 1.mid. Also the velocity in 2.mid seems to be different for each note.
for pitch, dur in zip(pitch_pred_seq_fmc, duration_pred_seq_fmc):
    fmc_seq.append({'event': 'note_on', 'note': pitch, 'start_time': current_time, 'duration': None, 'velocity': velocity})
    fmc_seq.append({'event': 'note_off', 'note': pitch, 'start_time': current_time, 'duration': dur, 'velocity': 0})
    current_time += dur

# TODO: QN: if we use multiple midi to train, what should be ticks_per_beat and tempo?
CreateMidi.create_midi_from_notes(fmc_output_path, fmc_seq, ticks_per_beat, tempo)

# second order
smc_output_name = input_fn.split(".")[0] + "_pred_smc.mid"
smc_output_path = os.path.join(output_dir, smc_output_name)
smc_seq = []
current_time = 0
# TODO: QN: What is the velocity? How to set it?
velocity = 110 # this is the one in 1.mid. Also the velocity in 2.mid seems to be different for each note.
for pitch, dur in zip(pitch_pred_seq_smc, duration_pred_seq_smc):
    smc_seq.append({'event': 'note_on', 'note': pitch, 'start_time': current_time, 'duration': None, 'velocity': velocity})
    smc_seq.append({'event': 'note_off', 'note': pitch, 'start_time': current_time, 'duration': dur, 'velocity': 0})
    current_time += dur

# TODO: QN: if we use multiple midi to train, what should be ticks_per_beat and tempo?
CreateMidi.create_midi_from_notes(smc_output_path, smc_seq, ticks_per_beat, tempo)