import numpy as np
import random
from typing import List, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns

class VanillaFirstOrderMarkovChain:
    """
    A first-order Markov chain model that can learn transition probabilities
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
        
        # Initialize count matrix and transition matrix
        self.count_matrix = np.zeros((self.n_states, self.n_states))
        self.transition_matrix = np.zeros((self.n_states, self.n_states))
            
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
        self.count_matrix = np.zeros((self.n_states, self.n_states))
        
        # Count transitions
        for sequence in sequences:
            for i in range(len(sequence) - 1):
                current_state = sequence[i]
                next_state = sequence[i + 1]
                
                if current_state not in self.state_to_idx:
                    raise ValueError(f"State '{current_state}' not in the state space.")
                if next_state not in self.state_to_idx:
                    raise ValueError(f"State '{next_state}' not in the state space.")
                
                current_idx = self.state_to_idx[current_state]
                next_idx = self.state_to_idx[next_state]

                if isPitch:
                    # Add weight for transition to be within octave
                    weight = (12-abs(current_state - next_state))/12
                    if weight >= 0:
                        self.count_matrix[current_idx, next_idx] += 2
                    else:
                        self.count_matrix[current_idx, next_idx] += 1
                    # if current_state != next_state+2 and current_state != next_state-2: # Add bias towards whole tone
                    #     self.count_matrix[current_idx, next_idx] += 1
                    # else:
                    #     self.count_matrix[current_idx, next_idx] += 2
                else:
                    if abs(current_state - next_state) > 10: # Add weight for similar duration +- 10
                        self.count_matrix[current_idx, next_idx] += 1
                    else:
                        self.count_matrix[current_idx, next_idx] += 2
                # self.count_matrix[current_idx, next_idx] += 1
        
        # Calculate probabilities from counts
        self._calculate_probabilities()
        self.is_fitted = True
    
    def _calculate_probabilities(self) -> None:
        """
        Calculate transition probabilities from count matrix.
        """
        # Make a copy to avoid modifying the counts
        self.transition_matrix = self.count_matrix.copy()
        
        # Normalize to get probabilities
        row_sums = self.transition_matrix.sum(axis=1, keepdims=True)
        # Avoid division by zero
        row_sums[row_sums == 0] = 1.0
        self.transition_matrix = self.transition_matrix / row_sums
    
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
            for i in range(len(sequence) - 1):
                current_state = sequence[i]
                next_state = sequence[i + 1]
                
                if current_state not in self.state_to_idx:
                    raise ValueError(f"State '{current_state}' not in the state space.")
                if next_state not in self.state_to_idx:
                    raise ValueError(f"State '{next_state}' not in the state space.")
                
                current_idx = self.state_to_idx[current_state]
                next_idx = self.state_to_idx[next_state]
                self.count_matrix[current_idx, next_idx] += 1
        
        # Recalculate probabilities from updated count matrix
        self._calculate_probabilities()
    
    def _get_initial_state(self, start_state: Optional[Any] = None, random_seed: Optional[int] = None) -> Any:
        """
        Helper function to handle the common pre-check logic for inference methods.
        
        Parameters:
        -----------
        start_state : state or None
            The starting state. If None, will be chosen randomly.
        random_seed : int or None
            Random seed for reproducibility.
            
        Returns:
        --------
        current_state : Any
            The starting state for the sequence.
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call calculate_transition_matrix first.")
        
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        if start_state is None:
            # Choose a random start state based on states that have outgoing transitions
            valid_start_indices = np.where(self.transition_matrix.sum(axis=1) > 0)[0]
            if len(valid_start_indices) == 0:
                raise ValueError("No valid start states found in the transition matrix.")
            start_idx = np.random.choice(valid_start_indices)
            current_state = self.idx_to_state[start_idx]
        else:
            if start_state not in self.state_to_idx:
                raise ValueError(f"Start state '{start_state}' not in the state space.")
            current_state = start_state
            
        return current_state
    
    def inference_prob(self, start_state: Optional[Any] = None, length: int = 10, 
                  random_seed: Optional[int] = None) -> List[Any]:
        """
        Generate a new sequence based on the learned transition probabilities,
        using weighted random selection according to transition probabilities.
        
        Parameters:
        -----------
        start_state : state or None
            The starting state. If None, will be chosen randomly.
        length : int
            The length of the sequence to generate.
        random_seed : int or None
            Random seed for reproducibility.
            
        Returns:
        --------
        sequence : list
            The generated sequence with probabilistic transitions.
        """
        current_state = self._get_initial_state(start_state, random_seed)
        sequence = [current_state]
        
        for _ in range(length - 1):
            current_idx = self.state_to_idx[current_state]
            probs = self.transition_matrix[current_idx]
            
            # If there are no transitions from current state, break
            if np.sum(probs) == 0:
                break
            
            next_idx = np.random.choice(self.n_states, p=probs)
            next_state = self.idx_to_state[next_idx]
            sequence.append(next_state)
            current_state = next_state
        
        return sequence
    
    def inference_max(self, start_state: Optional[Any] = None, length: int = 10) -> List[Any]:
        """
        Generate a new sequence based on the learned transition probabilities,
        always selecting the next state with the highest transition probability.
        
        Parameters:
        -----------
        start_state : state or None
            The starting state. If None, will be chosen randomly from states with outgoing transitions.
        length : int
            The length of the sequence to generate.
            
        Returns:
        --------
        sequence : list
            The generated sequence with maximum probability transitions.
        """
        # Use None as random_seed since inference_max doesn't use randomness for state selection
        current_state = self._get_initial_state(start_state)
        sequence = [current_state]
        
        for _ in range(length - 1):
            current_idx = self.state_to_idx[current_state]
            probs = self.transition_matrix[current_idx]
            
            # If there are no transitions from current state, break
            if np.sum(probs) == 0:
                break
            
            # Choose the next state with the highest probability
            next_idx = np.argmax(probs)
            next_state = self.idx_to_state[next_idx]
            sequence.append(next_state)
            current_state = next_state
        
        return sequence
    
    def get_transition_matrix(self) -> np.ndarray:
        """
        Get the transition matrix.
        
        Returns:
        --------
        transition_matrix : numpy.ndarray
            The transition probability matrix.
        """
        return self.transition_matrix
    
    def get_count_matrix(self) -> np.ndarray:
        """
        Get the count matrix.
        
        Returns:
        --------
        count_matrix : numpy.ndarray
            The matrix containing counts of transitions.
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
        Visualize the transition matrix as a heatmap.
        
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
            
        # Create labels for the states
        labels = [str(state) for state in self.state_space]
        
        # Create a figure and axis
        plt.figure(figsize=(10, 8))
        
        # Create the heatmap
        ax = sns.heatmap(
            self.transition_matrix,
            annot=True,
            fmt='.2f',
            cmap='viridis',
            xticklabels=labels,
            yticklabels=labels,
            vmin=0, 
            vmax=1.0
        )
        
        # Set title and labels
        plt.title('Transition Matrix Heatmap')
        plt.xlabel('To State')
        plt.ylabel('From State')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if a path is provided
        if save_path:
            plt.savefig(save_path)
            
        # Return the figure
        return plt.gcf()
