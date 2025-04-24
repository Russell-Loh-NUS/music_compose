import numpy as np
import random
from typing import List, Optional, Any, Dict, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class VanillaSecondOrderMarkovChain:
    """
    A second-order Markov chain model that can learn transition probabilities
    from sequences and generate new sequences based on the learned model.
    """
    
    def __init__(self, state_space: List[Any]):
        """
        Initialize the Markov chain model.
        
        Parameters:
        -----------
        state_space : list
            List of possible states. Must be provided.
        """
        if state_space is None or len(state_space) == 0:
            raise ValueError("state_space must be provided and non-empty")
            
        self.state_space = state_space
        self.state_to_idx = {state: idx for idx, state in enumerate(state_space)}
        self.idx_to_state = {idx: state for idx, state in enumerate(state_space)}
        self.n_states = len(state_space)
        
        # For second-order Markov chains, we need to track transitions from pairs of states
        # Using a dictionary of dictionaries for sparse representation
        self.count_matrix = {}
        self.transition_matrix = {}
        
        # Initialize transition matrices for all possible state pairs
        for i in range(self.n_states):
            for j in range(self.n_states):
                state_pair = (self.idx_to_state[i], self.idx_to_state[j])
                self.count_matrix[state_pair] = {state: 0 for state in state_space}
                self.transition_matrix[state_pair] = {state: 0.0 for state in state_space}
            
        self.is_fitted = False
    
    def calculate_transition_matrix(self, sequences: List[List[Any]], isPitch = True) -> None:
        """
        Calculate the transition matrix from sequences of states.
        
        Parameters:
        -----------
        sequences : list of lists
            List of sequences, where each sequence is a list of states.
        """
        # Initialize count matrix
        for state_pair in self.count_matrix:
            for state in self.state_space:
                self.count_matrix[state_pair][state] = 0
        
        # Count transitions
        for sequence in sequences:
            for i in range(len(sequence) - 2):  # Need at least 3 states for 2nd order
                first_state = sequence[i]
                second_state = sequence[i + 1]
                next_state = sequence[i + 2]
                
                if first_state not in self.state_to_idx:
                    raise ValueError(f"State '{first_state}' not in the state space.")
                if second_state not in self.state_to_idx:
                    raise ValueError(f"State '{second_state}' not in the state space.")
                if next_state not in self.state_to_idx:
                    raise ValueError(f"State '{next_state}' not in the state space.")
                
                state_pair = (first_state, second_state)

                if isPitch:
                    # Add weight transition to be within octave
                    # First state
                    weight = (12-abs(first_state - next_state))/12
                    if weight >= 0:
                        self.count_matrix[state_pair][next_state] += 2
                    else:
                        self.count_matrix[state_pair][next_state] += 1
                    # Second state
                    weight = (12-abs(second_state - next_state))/12
                    if weight >= 0:
                        self.count_matrix[state_pair][next_state] += 2
                    else:
                        self.count_matrix[state_pair][next_state] += 1
                else:
                    # First state
                    if abs(first_state - next_state) > 10: # Add weight for similar duration +- 10
                        self.count_matrix[state_pair][next_state] += 1
                    else:
                        self.count_matrix[state_pair][next_state] += 2
                    # Second state
                    if abs(second_state - next_state) > 10: # Add weight for similar duration +- 10
                        self.count_matrix[state_pair][next_state] += 1
                    else:
                        self.count_matrix[state_pair][next_state] += 2
                
                # self.count_matrix[state_pair][next_state] += 1
                
        
        # Calculate probabilities from counts
        self._calculate_probabilities()
        self.is_fitted = True
    
    def _calculate_probabilities(self) -> None:
        """
        Calculate transition probabilities from count matrix.
        """
        for state_pair in self.count_matrix:
            # Get total counts for this state pair
            total_count = sum(self.count_matrix[state_pair].values())
            
            # Calculate probabilities
            for next_state in self.state_space:
                if total_count > 0:
                    self.transition_matrix[state_pair][next_state] = self.count_matrix[state_pair][next_state] / total_count
                else:
                    # Uniform distribution if no transitions observed
                    self.transition_matrix[state_pair][next_state] = 1.0 / self.n_states
    
    def update_transition_matrix(self, new_sequences: List[List[Any]]) -> None:
        """
        Update the transition matrix with new sequences.
        
        Parameters:
        -----------
        new_sequences : list of lists
            New sequences to update the model with.
        """
        if not self.is_fitted:
            self.calculate_transition_matrix(new_sequences)
            return
        
        # Count new transitions and add to existing count matrix
        for sequence in new_sequences:
            for i in range(len(sequence) - 2):
                first_state = sequence[i]
                second_state = sequence[i + 1]
                next_state = sequence[i + 2]
                
                if first_state not in self.state_to_idx:
                    raise ValueError(f"State '{first_state}' not in the state space.")
                if second_state not in self.state_to_idx:
                    raise ValueError(f"State '{second_state}' not in the state space.")
                if next_state not in self.state_to_idx:
                    raise ValueError(f"State '{next_state}' not in the state space.")
                
                state_pair = (first_state, second_state)
                self.count_matrix[state_pair][next_state] += 1
        
        # Recalculate probabilities from updated count matrix
        self._calculate_probabilities()
    
    def _get_initial_state_pair(self, start_state: Optional[Tuple[Any, Any]] = None, 
                               random_seed: Optional[int] = None) -> Tuple[Any, Any]:
        """
        Helper function to handle the common pre-check logic for inference methods.
        
        Parameters:
        -----------
        start_state : tuple(state, state) or None
            The starting state pair. If None, will be chosen randomly.
        random_seed : int or None
            Random seed for reproducibility.
            
        Returns:
        --------
        current_state_pair : tuple(Any, Any)
            The starting state pair for the sequence.
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call calculate_transition_matrix first.")
        
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        if start_state is None:
            # Find state pairs that have outgoing transitions
            valid_state_pairs = []
            for state_pair in self.transition_matrix:
                if any(prob > 0 for prob in self.transition_matrix[state_pair].values()):
                    valid_state_pairs.append(state_pair)
            
            if not valid_state_pairs:
                raise ValueError("No valid state pairs found with outgoing transitions.")
            
            # Choose a random state pair
            current_state_pair = random.choice(valid_state_pairs)
        else:
            first_state, second_state = start_state
            if first_state not in self.state_to_idx:
                raise ValueError(f"First state '{first_state}' not in the state space.")
            if second_state not in self.state_to_idx:
                raise ValueError(f"Second state '{second_state}' not in the state space.")
            current_state_pair = start_state
            
        return current_state_pair
    
    def inference_prob(self, start_state: Optional[Tuple[Any, Any]] = None, length: int = 10, 
                      random_seed: Optional[int] = None) -> List[Any]:
        """
        Generate a new sequence based on the learned transition probabilities,
        using weighted random selection according to transition probabilities.
        
        Parameters:
        -----------
        start_state : tuple(state, state) or None
            The starting state pair. If None, will be chosen randomly.
        length : int
            The length of the sequence to generate.
        random_seed : int or None
            Random seed for reproducibility.
            
        Returns:
        --------
        sequence : list
            The generated sequence with probabilistic transitions.
        """
        current_state_pair = self._get_initial_state_pair(start_state, random_seed)
        # Start with the initial pair of states
        sequence = list(current_state_pair)
        
        for _ in range(length - 2):  # -2 because we already have the first two states
            # Get transition probabilities from the current state pair
            probs = self.transition_matrix[current_state_pair]
            
            # Convert to list for np.random.choice
            states = list(probs.keys())
            probabilities = [probs[state] for state in states]
            
            # Normalize probabilities (ensure they sum to 1)
            prob_sum = sum(probabilities)
            if prob_sum == 0:
                break  # No transitions available
                
            normalized_probs = [p/prob_sum for p in probabilities]
            
            # Choose next state based on probabilities
            next_state = np.random.choice(states, p=normalized_probs)
            sequence.append(next_state)
            
            # Update current state pair for next iteration
            current_state_pair = (current_state_pair[1], next_state)
        
        return sequence
    
    def inference_max(self, start_state: Optional[Tuple[Any, Any]] = None, length: int = 10) -> List[Any]:
        """
        Generate a new sequence based on the learned transition probabilities,
        always selecting the next state with the highest transition probability.
        
        Parameters:
        -----------
        start_state : tuple(state, state) or None
            The starting state pair. If None, will be chosen randomly from pairs with outgoing transitions.
        length : int
            The length of the sequence to generate.
            
        Returns:
        --------
        sequence : list
            The generated sequence with maximum probability transitions.
        """
        current_state_pair = self._get_initial_state_pair(start_state)
        # Start with the initial pair of states
        sequence = list(current_state_pair)
        
        for _ in range(length - 2):  # -2 because we already have the first two states
            # Get transition probabilities from the current state pair
            probs = self.transition_matrix[current_state_pair]
            
            # Find the state with the highest probability
            if all(p == 0 for p in probs.values()):
                break  # No transitions available
                
            next_state = max(probs.items(), key=lambda x: x[1])[0]
            sequence.append(next_state)
            
            # Update current state pair for next iteration
            current_state_pair = (current_state_pair[1], next_state)
        
        return sequence
    
    def get_transition_matrix(self) -> Dict[Tuple[Any, Any], Dict[Any, float]]:
        """
        Get the transition matrix.
        
        Returns:
        --------
        transition_matrix : dict
            The transition probability matrix as a nested dictionary.
            {(state1, state2): {next_state: probability}}
        """
        return self.transition_matrix
    
    def get_count_matrix(self) -> Dict[Tuple[Any, Any], Dict[Any, int]]:
        """
        Get the count matrix.
        
        Returns:
        --------
        count_matrix : dict
            The matrix containing counts of transitions as a nested dictionary.
            {(state1, state2): {next_state: count}}
        """
        return self.count_matrix
    
    def get_state_space(self) -> List[Any]:
        """
        Get the state space.
        
        Returns:
        --------
        state_space : list
            The list of states.
        """
        return self.state_space
    
    def visualize_transition_matrix(self, save_path=None):
        """
        Visualize the transition matrix as a confusion matrix-style heatmap.
        For second-order Markov chains, we visualize the most frequent state pairs.
        
        Parameters:
        -----------
        save_path : str or None
            If provided, save the visualization to this path.
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            The figure containing the visualization.
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call calculate_transition_matrix first.")
        
        # Get top state pairs by transition count
        pair_counts = {}
        for state_pair, counts in self.count_matrix.items():
            pair_counts[state_pair] = sum(counts.values())
            
        # Sort pairs by count and take top 15 (or fewer if there are less than 15)
        num_pairs = min(15, len(pair_counts))
        top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:num_pairs]
        top_pair_states = [pair[0] for pair in top_pairs]
        
        # Get top next states
        next_state_counts = {}
        for state in self.state_space:
            count = 0
            for state_pair in top_pair_states:
                count += self.count_matrix[state_pair][state]
            next_state_counts[state] = count
            
        top_next_states = sorted(next_state_counts.items(), key=lambda x: x[1], reverse=True)[:num_pairs]
        top_next = [state[0] for state in top_next_states]
        
        # Create a matrix of transition probabilities for the top pairs and next states
        matrix_data = np.zeros((len(top_pair_states), len(top_next)))
        
        for i, state_pair in enumerate(top_pair_states):
            for j, next_state in enumerate(top_next):
                matrix_data[i, j] = self.transition_matrix[state_pair][next_state]
        
        # Create a DataFrame for better visualization
        pair_labels = [f"({s1},{s2})" for s1, s2 in top_pair_states]
        next_labels = [str(s) for s in top_next]
        
        df = pd.DataFrame(matrix_data, index=pair_labels, columns=next_labels)
        
        # Create the heatmap visualization
        plt.figure(figsize=(12, 10))
        ax = sns.heatmap(
            df,
            annot=True,
            fmt='.2f',
            cmap='viridis',
            vmin=0,
            vmax=max(0.3, matrix_data.max()),  # Cap at 0.3 or the max value if higher
            cbar_kws={'label': 'Transition Probability'}
        )
        
        # Set title and labels
        plt.title('Second-Order Markov Chain Transition Matrix\n(Top State Pairs → Top Next States)', fontsize=16)
        plt.xlabel('Next State', fontsize=14)
        plt.ylabel('Current State Pair (Previous, Current)', fontsize=14)
        
        # Rotate x-axis labels if they're crowded
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if a path is provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        # Return the figure
        return plt.gcf()
