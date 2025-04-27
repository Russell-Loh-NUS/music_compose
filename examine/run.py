import numpy as np
import matplotlib.pyplot as plt
from extract_midi import ExtractMidi

class ExamineHarmonicDissonance():
    def __init__(self):
        self.pitch_sequence = []
        self.duration_sequence = []


    def set_up_harmonic_matrix(self):
        interval_weights = {
            0: 1.0, 
            7: 0.9, 
            5: 0.8, 
            4: 0.7, 
            3: 0.6,
            8: 0.5, 
            9: 0.5, 
            2: 0.2, 
            10: 0.2, 
            6: -0.8,
            1: -0.5, 
            11: -0.3,
        }

        self.score_matrix = np.zeros((88, 88))

        for i in range(88):
            for j in range(88):
                pitch1 = i + 21  # MIDI note
                pitch2 = j + 21
                interval = abs(pitch1 - pitch2) % 12
                self.score_matrix[i][j] = interval_weights.get(interval, 0)
    

    def read_input_file(self, input_path):
        _, _, _, notes = ExtractMidi.extract_midi_data(input_path) # Extract the midi data. The notes will be in order of start time.
        for note in notes:
            # Collect pitch and duration sequences
            self.pitch_sequence.append(note['note'])
            self.duration_sequence.append(note['duration'])


    def get_harmonic_dissonance(self, name, save_path=None):
        self.set_up_harmonic_matrix()

        pitches = []
        for pitch, dur in zip(self.pitch_sequence, self.duration_sequence):
            pitches.append(pitch)
        
        scores = []
        for i in range(len(pitches)):
            pitch_i = pitches[i]
            pitch_j = pitches[i + 1] if i + 1 < len(pitches) else pitches[0]
            if pitch_i < 21 or pitch_i > 108:
                print("Invalid pitch: " + str(pitch))
                continue
            if pitch_j < 21 or pitch_j > 108:
                print("Invalid pitch: " + str(pitch))
                continue
            # Calculate the harmonic score
            score = self.score_matrix[pitch_i-21][pitch_j-21]
            # print("Harmonic score between " + str(pitch_i) + " and " + str(pitch_j) + ": " + str(score))
            scores.append(score)
        average_score = round(sum(scores) / len(scores), 4)

        print("Harmonic scores of " + name + ": " + str(average_score))
        self.plot_harmonic_scores(scores, "Harmonic scroes is " + str(average_score), save_path)
        

    def plot_harmonic_scores(self, scores, label_content, save_path=None):
        # plt.figure(figsize=(10, 6))
        # plt.plot(scores, marker='o', linestyle='-', color='blue')
        # plt.title("Harmonic Scores Over Time", fontsize=16)
        # plt.xlabel("Time Step", fontsize=14)
        # plt.ylabel("Harmonic Score", fontsize=14)
        # plt.grid(True)
        # plt.tight_layout()
        # if save_path:
        #     plt.savefig(save_path, dpi=300, bbox_inches='tight')

        plt.figure(figsize=(10, 6))
        plt.plot(scores, marker='o', linestyle='-', color='blue')
        plt.title("Harmonic Scores Over Time", fontsize=16)
        plt.xlabel("Time Step", fontsize=14)
        plt.ylabel("Harmonic Score", fontsize=14)
        plt.grid(True)
        
        # Add text below the figure
        plt.figtext(0.5,                  # x-position (0.5 = center)
                    0.01,                 # y-position (just above bottom)
                    label_content,        # Your text content
                    ha='center',          # Horizontal alignment
                    va='bottom',          # Vertical alignment
                    fontsize=12)          # Font size
        
        plt.tight_layout()
        
        # Adjust subplot to make room for the text
        plt.subplots_adjust(bottom=0.15)  # Increase bottom margin
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to prevent display if not needed