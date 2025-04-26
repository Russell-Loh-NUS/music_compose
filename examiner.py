import os
from examine.run import ExamineHarmonicDissonance

examiner = ExamineHarmonicDissonance()
input_folder = 'demo_sample'
first_order_input_fn = "275_first_order.mid"
second_order_input_fn = "275_second_order.mid"
first_order_input_path = os.path.join(input_folder, first_order_input_fn)
second_order_input_path = os.path.join(input_folder, second_order_input_fn)

examiner.read_input_file(first_order_input_path)
examiner.get_harmonic_dissonance(first_order_input_fn, save_path="demo_sample/harmonic_scores_first_order.png")
examiner.read_input_file(second_order_input_path)
examiner.get_harmonic_dissonance(second_order_input_fn, save_path="demo_sample/harmonic_scores_second_order.png")
