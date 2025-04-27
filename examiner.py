import os
from examine.run import ExamineHarmonicDissonance

examiner = ExamineHarmonicDissonance()
file_name_list = {
    "original": os.path.join("midi_files/training", "1 (5).mid"),
    "result_first_order": os.path.join("demo_sample", "275_first_order.mid"),
    "result_second_order": os.path.join("demo_sample", "275_second_order.mid"),
    "result_post_processing": os.path.join("demo_sample/post_processing", "(5) First Order FMajor + Chord + Band.mid"),
}
for name, file_name in file_name_list.items():
    examiner = ExamineHarmonicDissonance()
    examiner.read_input_file(file_name)
    examiner.get_harmonic_dissonance(name, save_path="demo_sample/examiner_results/" + name + "_harmonic_scores.png")
