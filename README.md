# Setting up
1. Ensure you have conda installed - https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html
2. On root directory, run `conda env create -f environment.yml`
3. Start conda environment by running `conda activate music_compose`
4. Run `main.py`. If you are using VS Code, remember to select the interpreter `music_compose` on the bottom right.

# Folder structure
- `main.py` entry point of the application.
- `midi_files` contain the sample midi files.

# Tools
1. To view midi sequence, use online tool: https://app.midiano.com/

# Sample Model Running
run `python run_model.py` to run learning and inferencing on a single midi file.

# Using the Markov Chain Models

## Available Models

1. **VanillaFirstOrderMarkovChain**: A first-order Markov model that predicts the next state based only on the current state.
2. **VanillaSecondOrderMarkovChain**: A second-order Markov model that predicts the next state based on the current state and the previous state.

### Basic Usage

Both models share a similar API, making it easy to switch between them:

```python
from model.VanillaFirstOrderMarkovChain import VanillaFirstOrderMarkovChain
from model.VanillaSecondOrderMarkovChain import VanillaSecondOrderMarkovChain

# Define your state space
states = [1, 2, 3, 4, 5]

# Create training sequence(s)
sequences = [[1, 2, 3, 2, 1, 2, 5, 4, 3, 2, 1]]

# Example 1: Using the First-Order Model
model1 = VanillaFirstOrderMarkovChain(states)
model1.calculate_transition_matrix(sequences)
generated_sequence = model1.inference_prob(length=10, random_seed=42)
print("First-order generated sequence:", generated_sequence)

# Example 2: Using the Second-Order Model
model2 = VanillaSecondOrderMarkovChain(states)
model2.calculate_transition_matrix(sequences)
generated_sequence = model2.inference_prob(length=10, random_seed=42)
print("Second-order generated sequence:", generated_sequence)
```

### Visualization

Both models include a visualization method for the transition matrix:

```python
# Visualize the transition matrices
model1.visualize_transition_matrix("first_order_transitions.png")
model2.visualize_transition_matrix("second_order_transitions.png")
```

The first-order model produces a standard heat map, while the second-order model creates a condensed visualization showing the most frequent state pairs and their transition probabilities.

Refer to `run_model.py` for sample usage.

### Model Selection and Differences

- **First-Order Model**: Simpler and uses less memory. Good for capturing basic patterns and when the dataset is small.
  
- **Second-Order Model**: Captures more complex patterns and context, producing more musically coherent results. Requires more training data to be effective.

### Advanced Features

Both models support:

1. **Inference with probabilities** (`inference_prob`): Randomly selects next states based on transition probabilities
2. **Inference with max probability** (`inference_max`): Always selects the most likely next state
3. **Updating the model** (`update_transition_matrix`): Add new training data without retraining from scratch
4. **Specifying a start state**: Control where the generated sequence begins

The second-order model's API is similar but requires state pairs instead of single states when specifying start states:

```python
# First-order model with specific start state
seq1 = model1.inference_prob(start_state=42, length=10)

# Second-order model with specific start state pair
seq2 = model2.inference_prob(start_state=(42, 47), length=10)
```