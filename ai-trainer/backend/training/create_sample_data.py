# create_sample_data.py

import numpy as np
from pathlib import Path

# ✅ TARGET DIRECTORY
SAVE_DIR = "data/videos"

def generate_squat_sequence(seq_len, feature_dim):
    base = np.zeros((seq_len, feature_dim))

    for t in range(seq_len):
        phase = np.sin(2 * np.pi * t / seq_len)

        # Simulate knee/hip angle variation
        base[t, 0:7] = phase

        # Add motion noise
        base[t] += np.random.normal(0, 0.05, feature_dim)

    return base


def generate_boxing_sequence(seq_len, feature_dim):
    base = np.zeros((seq_len, feature_dim))

    for t in range(seq_len):
        punch = (t % 10) / 10.0

        # Simulate arm extension (bone vectors)
        base[t, 7:20] = punch

        base[t] += np.random.normal(0, 0.05, feature_dim)

    return base


def generate_jumping_sequence(seq_len, feature_dim):
    base = np.zeros((seq_len, feature_dim))

    for t in range(seq_len):
        jump = abs(np.sin(2 * np.pi * t / seq_len))

        # Simulate vertical motion (velocity features)
        base[t, 50:80] = jump

        base[t] += np.random.normal(0, 0.05, feature_dim)

    return base


def generate_waving_sequence(seq_len, feature_dim):
    base = np.zeros((seq_len, feature_dim))

    for t in range(seq_len):
        wave = np.sin(4 * np.pi * t / seq_len)

        # Simulate hand movement
        base[t, 20:40] = wave

        base[t] += np.random.normal(0, 0.05, feature_dim)

    return base


def create_sample_dataset(output_dir: str, num_sequences: int = 200):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    feature_dim = 175
    sequence_length = 30

    sequences = []
    phase_labels = []
    error_labels = []
    score_labels = []

    exercises = ["squat", "boxing", "jumping", "waving"]

    print(f"Creating exercise-aware dataset...")

    for i in range(num_sequences):

        exercise = np.random.choice(exercises)

        if exercise == "squat":
            seq = generate_squat_sequence(sequence_length, feature_dim)
            phase = np.random.randint(0, 4)

        elif exercise == "boxing":
            seq = generate_boxing_sequence(sequence_length, feature_dim)
            phase = np.random.randint(0, 2)

        elif exercise == "jumping":
            seq = generate_jumping_sequence(sequence_length, feature_dim)
            phase = np.random.randint(0, 2)

        elif exercise == "waving":
            seq = generate_waving_sequence(sequence_length, feature_dim)
            phase = np.random.randint(0, 2)

        sequences.append(seq)
        phase_labels.append(phase)

        # Errors (random but realistic low probability)
        errors = np.random.binomial(1, 0.1, size=3)
        error_labels.append(errors)

        # Score biased high (good form)
        score_labels.append(np.random.uniform(0.7, 1.0))

    sequences = np.array(sequences, dtype=np.float32)
    phase_labels = np.array(phase_labels)
    error_labels = np.array(error_labels, dtype=np.float32)
    score_labels = np.array(score_labels, dtype=np.float32)

    # Save
    np.save(output_dir / "sequences.npy", sequences)
    np.save(output_dir / "phase_sample_labels.npy", phase_labels)
    np.save(output_dir / "error_sample_labels.npy", error_labels)
    np.save(output_dir / "score_sample_labels.npy", score_labels)

    print(f"\n✅ Dataset Created:")
    print(f"Sequences: {sequences.shape}")
    print(f"Saved to: {output_dir}")


if __name__ == "__main__":
    create_sample_dataset(SAVE_DIR, num_sequences=300)
