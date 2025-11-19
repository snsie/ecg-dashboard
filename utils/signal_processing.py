"""Signal processing functions for ECG analysis."""

import numpy as np
from scipy import signal
from typing import Tuple, List, Dict


def bandpass_filter(
    ecg_signal: np.ndarray,
    fs: float,
    lowcut: float = 0.5,
    highcut: float = 40.0,
    order: int = 4
) -> np.ndarray:
    """
    Apply a Butterworth bandpass filter to the ECG signal.
    
    Args:
        ecg_signal: Input ECG signal
        fs: Sampling frequency in Hz
        lowcut: Low cutoff frequency in Hz
        highcut: High cutoff frequency in Hz
        order: Filter order
        
    Returns:
        Filtered ECG signal
    """
    # Normalize frequencies to Nyquist frequency
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # Design the Butterworth filter
    b, a = signal.butter(order, [low, high], btype='band')
    
    # Apply the filter
    filtered_signal = signal.filtfilt(b, a, ecg_signal)
    
    return filtered_signal


def detect_r_peaks(
    ecg_signal: np.ndarray,
    fs: float,
    threshold: float = 0.6,
    min_distance: float = 0.4
) -> np.ndarray:
    """
    Detect R-peaks in the ECG signal using scipy's find_peaks.
    
    Args:
        ecg_signal: Input ECG signal (preferably filtered)
        fs: Sampling frequency in Hz
        threshold: Relative threshold for peak detection (0-1)
        min_distance: Minimum distance between peaks in seconds
        
    Returns:
        Array of peak indices
    """
    # Calculate absolute threshold
    signal_range = np.max(ecg_signal) - np.min(ecg_signal)
    abs_threshold = np.min(ecg_signal) + threshold * signal_range
    
    # Convert minimum distance to samples
    min_distance_samples = int(min_distance * fs)
    
    # Find peaks
    peaks, properties = signal.find_peaks(
        ecg_signal,
        height=abs_threshold,
        distance=min_distance_samples
    )
    
    return peaks


def compute_heart_rate(
    peak_indices: np.ndarray,
    fs: float
) -> Dict[str, float]:
    """
    Compute heart rate statistics from detected R-peaks.
    
    Args:
        peak_indices: Array of R-peak indices
        fs: Sampling frequency in Hz
        
    Returns:
        Dictionary with heart rate statistics
    """
    if len(peak_indices) < 2:
        return {
            'mean_bpm': 0.0,
            'min_bpm': 0.0,
            'max_bpm': 0.0,
            'std_bpm': 0.0,
            'num_beats': len(peak_indices)
        }
    
    # Calculate RR intervals (in seconds)
    rr_intervals = np.diff(peak_indices) / fs
    
    # Convert to instantaneous heart rates (BPM)
    instantaneous_hr = 60.0 / rr_intervals
    
    # Calculate statistics
    stats = {
        'mean_bpm': float(np.mean(instantaneous_hr)),
        'min_bpm': float(np.min(instantaneous_hr)),
        'max_bpm': float(np.max(instantaneous_hr)),
        'std_bpm': float(np.std(instantaneous_hr)),
        'num_beats': len(peak_indices),
        'mean_rr_interval': float(np.mean(rr_intervals))
    }
    
    return stats


def compute_hrv_metrics(
    peak_indices: np.ndarray,
    fs: float
) -> Dict[str, float]:
    """
    Compute basic heart rate variability (HRV) metrics.
    
    Args:
        peak_indices: Array of R-peak indices
        fs: Sampling frequency in Hz
        
    Returns:
        Dictionary with HRV metrics
    """
    if len(peak_indices) < 2:
        return {
            'sdnn': 0.0,
            'rmssd': 0.0
        }
    
    # Calculate RR intervals (in milliseconds)
    rr_intervals = np.diff(peak_indices) / fs * 1000.0
    
    # SDNN: Standard deviation of NN intervals
    sdnn = float(np.std(rr_intervals, ddof=1))
    
    # RMSSD: Root mean square of successive differences
    diff_rr = np.diff(rr_intervals)
    rmssd = float(np.sqrt(np.mean(diff_rr ** 2)))
    
    return {
        'sdnn': sdnn,
        'rmssd': rmssd
    }
