"""Data loading and synthetic ECG generation utilities."""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple


def generate_synthetic_ecg(
    duration: float = 10.0,
    sampling_rate: int = 360,
    heart_rate: float = 72.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a synthetic ECG-like signal.
    
    Args:
        duration: Signal duration in seconds
        sampling_rate: Sampling frequency in Hz
        heart_rate: Average heart rate in BPM
        
    Returns:
        Tuple of (time_array, ecg_signal)
    """
    # Time array
    t = np.arange(0, duration, 1/sampling_rate)
    
    # Initialize signal
    ecg = np.zeros_like(t)
    
    # Calculate beat period
    beat_period = 60.0 / heart_rate  # seconds per beat
    
    # Generate R-peaks at regular intervals with slight variation
    num_beats = int(duration / beat_period)
    
    for i in range(num_beats):
        # Add slight random variation to beat timing
        beat_time = i * beat_period + np.random.normal(0, 0.02)
        
        if beat_time >= duration:
            break
            
        # Find closest index
        peak_idx = int(beat_time * sampling_rate)
        
        if peak_idx >= len(t):
            continue
        
        # Create one cardiac cycle around this peak
        # P wave (small positive deflection)
        p_start = peak_idx - int(0.16 * sampling_rate)
        p_end = peak_idx - int(0.08 * sampling_rate)
        if p_start >= 0 and p_end < len(ecg):
            p_indices = np.arange(p_start, p_end)
            p_wave = 0.15 * np.sin(np.pi * (p_indices - p_start) / (p_end - p_start))
            ecg[p_indices] += p_wave
        
        # QRS complex (sharp peak)
        qrs_start = peak_idx - int(0.04 * sampling_rate)
        qrs_end = peak_idx + int(0.04 * sampling_rate)
        if qrs_start >= 0 and qrs_end < len(ecg):
            qrs_indices = np.arange(qrs_start, qrs_end)
            # Q wave (small negative)
            q_indices = qrs_indices[:len(qrs_indices)//3]
            ecg[q_indices] += -0.2 * np.sin(np.pi * np.arange(len(q_indices)) / len(q_indices))
            # R wave (large positive)
            r_indices = qrs_indices[len(qrs_indices)//3:2*len(qrs_indices)//3]
            ecg[r_indices] += 1.5 * np.sin(np.pi * np.arange(len(r_indices)) / len(r_indices))
            # S wave (small negative)
            s_indices = qrs_indices[2*len(qrs_indices)//3:]
            ecg[s_indices] += -0.3 * np.sin(np.pi * np.arange(len(s_indices)) / len(s_indices))
        
        # T wave (broader positive deflection)
        t_start = peak_idx + int(0.08 * sampling_rate)
        t_end = peak_idx + int(0.24 * sampling_rate)
        if t_start >= 0 and t_end < len(ecg):
            t_indices = np.arange(t_start, t_end)
            t_wave = 0.3 * np.sin(np.pi * (t_indices - t_start) / (t_end - t_start))
            ecg[t_indices] += t_wave
    
    # Add baseline wander (low frequency component)
    baseline = 0.05 * np.sin(2 * np.pi * 0.3 * t)
    
    # Add some noise
    noise = np.random.normal(0, 0.03, len(t))
    
    # Combine components
    ecg = ecg + baseline + noise
    
    return t, ecg


def load_ecg_data(path: str) -> pd.DataFrame:
    """
    Load ECG data from a CSV file.
    
    Args:
        path: Path to the CSV file
        
    Returns:
        DataFrame with 'time' and 'ecg' columns
    """
    try:
        df = pd.read_csv(path)
        
        # Ensure required columns exist
        if 'time' not in df.columns or 'ecg' not in df.columns:
            raise ValueError("CSV must contain 'time' and 'ecg' columns")
        
        return df
    
    except Exception as e:
        raise RuntimeError(f"Failed to load ECG data from {path}: {str(e)}")


def save_synthetic_ecg(path: str, duration: float = 30.0, sampling_rate: int = 360):
    """
    Generate and save synthetic ECG data to a CSV file.
    
    Args:
        path: Output path for the CSV file
        duration: Signal duration in seconds
        sampling_rate: Sampling frequency in Hz
    """
    t, ecg = generate_synthetic_ecg(duration=duration, sampling_rate=sampling_rate)
    
    df = pd.DataFrame({
        'time': t,
        'ecg': ecg
    })
    
    # Create directory if it doesn't exist
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(path, index=False)
    print(f"Synthetic ECG data saved to {path}")


if __name__ == "__main__":
    # Generate sample data
    save_synthetic_ecg("data/sample_ecg.csv", duration=30.0)
