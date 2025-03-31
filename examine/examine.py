import numpy as np

def frequency(p):
    """calculate corresponding frequency of p (based on A0 = 27.5 Hz)"""
    return 27.5 * (2 ** ((p - 1) / 12))

def harmonic_ratio(p1, p2):
    """calculate the harmonic ratio between two notes p1 and p2"""
    f1, f2 = frequency(p1), frequency(p2)
    simple_ratios = [2/1, 3/2, 4/3, 5/4, 6/5]
    closest_ratio = min(simple_ratios, key=lambda r: abs(f1/f2 - r))
    return 1 / (abs(f1/f2 - closest_ratio) + 1e-6)  # avoid division by zero

def dissonance(p1, p2, alpha=0.1):
    """calculate the dissonance between two notes p1 and p2"""
    f1, f2 = frequency(p1), frequency(p2)
    return np.exp(-alpha * abs(f1 - f2))

def harmony_scale(scale):
    """calculate the overall harmony of a set of notes"""
    harmony_score = 0
    for i in range(len(scale)):
        for j in range(i + 1, len(scale)):
            harmony_score += harmonic_ratio(scale[i], scale[j])
    return harmony_score

def dissonance_scale(scale, alpha=0.1):
    """caculate the overall dissonance of a set of notes"""
    dissonance_score = 0
    for i in range(len(scale)):
        for j in range(i + 1, len(scale)):
            dissonance_score += dissonance(scale[i], scale[j], alpha)
    return dissonance_score

def harmonic_dissonance_analysis(scale):
    """perform harmonic and dissonance analysis on a scale"""
    harmony = harmony_scale(scale)
    dissonance = dissonance_scale(scale)

    return harmony, dissonance

def check_harmonic_dissonance_score(harmony_score, dissonance_score, threshold=0.5):
    """check if the harmonic score is greater than the dissonance score"""
    if harmony_score > 10.0 and dissonance_score < 2.0:
        return "Perfect Harmony"
    elif 5.0 <= harmony_score <= 10.0 and 2.0 <=dissonance_score <= 5.0:
        return "Balanced Harmony"
    elif harmony_score < 5.0 and dissonance_score > 5.0:
        return "Dissonance"

# example: C major scale (C, D, E, F, G, A, B, C)
c_major_scale = [40, 42, 44, 45, 47, 49, 51, 52]
harmony_score, dissonance_score = harmonic_dissonance_analysis(c_major_scale)
print("Harmony Score: %.4f" % harmony_score)
print("Dissonance Score: %.4f" % dissonance_score)