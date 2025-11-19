"""
ECG Dashboard - Interactive Biomedical Signal Analysis
A Streamlit application for visualizing and analyzing ECG signals.
"""

import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path

# Import utility functions
from utils.data_loader import load_ecg_data, generate_synthetic_ecg, save_synthetic_ecg
from utils.signal_processing import bandpass_filter, detect_r_peaks, compute_heart_rate, compute_hrv_metrics
from utils.plotting import create_ecg_plot, create_comparison_plot, create_heart_rate_plot


# Page configuration
st.set_page_config(
    page_title="ECG Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def ensure_data_exists():
    """Ensure that sample ECG data exists, generate if needed."""
    data_path = Path("data/sample_ecg.csv")
    
    if not data_path.exists():
        st.info("Generating synthetic ECG data...")
        save_synthetic_ecg(str(data_path), duration=30.0, sampling_rate=360)
    
    return str(data_path)


def main():
    """Main application function."""
    
    # Title and description
    st.title("❤️ ECG Signal Analysis Dashboard")
    st.markdown("""
    This interactive dashboard allows you to visualize and analyze **Electrocardiogram (ECG)** signals.
    An ECG measures the electrical activity of the heart and is crucial for detecting cardiac abnormalities,
    monitoring heart rate, and assessing overall cardiovascular health.
    """)
    
    # Sidebar controls
    st.sidebar.header("⚙️ Control Panel")
    
    # Data loading
    data_path = ensure_data_exists()
    
    try:
        # Load data
        df = load_ecg_data(data_path)
        time = df['time'].values
        ecg_raw = df['ecg'].values
        
        # Determine sampling rate
        if len(time) > 1:
            fs = 1.0 / (time[1] - time[0])
        else:
            fs = 360.0  # Default
        
        st.sidebar.success(f"✅ Data loaded successfully")
        st.sidebar.metric("Sampling Rate", f"{fs:.0f} Hz")
        st.sidebar.metric("Duration", f"{time[-1]:.1f} seconds")
        st.sidebar.metric("Total Samples", len(time))
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Generating new synthetic data...")
        save_synthetic_ecg(data_path, duration=30.0, sampling_rate=360)
        df = load_ecg_data(data_path)
        time = df['time'].values
        ecg_raw = df['ecg'].values
        fs = 360.0
    
    # Time window selection
    st.sidebar.subheader("📊 Time Window Selection")
    time_range = st.sidebar.slider(
        "Select time range (seconds)",
        min_value=float(time[0]),
        max_value=float(time[-1]),
        value=(float(time[0]), min(10.0, float(time[-1]))),
        step=0.5
    )
    
    # Filter time window
    time_mask = (time >= time_range[0]) & (time <= time_range[1])
    time_window = time[time_mask]
    ecg_window = ecg_raw[time_mask]
    
    # Filter parameters
    st.sidebar.subheader("🔧 Filter Parameters")
    lowcut = st.sidebar.slider(
        "Low cutoff frequency (Hz)",
        min_value=0.1,
        max_value=5.0,
        value=0.5,
        step=0.1
    )
    highcut = st.sidebar.slider(
        "High cutoff frequency (Hz)",
        min_value=10.0,
        max_value=100.0,
        value=40.0,
        step=5.0
    )
    
    # Apply bandpass filter
    try:
        ecg_filtered = bandpass_filter(ecg_window, fs, lowcut, highcut)
    except Exception as e:
        st.error(f"Error applying filter: {str(e)}")
        ecg_filtered = ecg_window
    
    # Peak detection parameters
    st.sidebar.subheader("🔍 Peak Detection")
    threshold = st.sidebar.slider(
        "Peak detection threshold",
        min_value=0.1,
        max_value=0.9,
        value=0.6,
        step=0.05,
        help="Relative threshold for detecting R-peaks (0-1)"
    )
    min_distance = st.sidebar.slider(
        "Minimum peak distance (seconds)",
        min_value=0.2,
        max_value=1.0,
        value=0.4,
        step=0.05,
        help="Minimum time between consecutive peaks"
    )
    
    # Detect R-peaks
    try:
        peaks = detect_r_peaks(ecg_filtered, fs, threshold, min_distance)
    except Exception as e:
        st.error(f"Error detecting peaks: {str(e)}")
        peaks = np.array([])
    
    # Compute heart rate statistics
    hr_stats = compute_heart_rate(peaks, fs)
    hrv_stats = compute_hrv_metrics(peaks, fs)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Raw Signal",
        "🔬 Filtered Signal & Peaks",
        "💓 Heart Rate Analysis",
        "📊 Summary Metrics"
    ])
    
    # Tab 1: Raw Signal
    with tab1:
        st.subheader("Raw ECG Signal")
        st.markdown("""
        This shows the original, unprocessed ECG signal. The signal may contain noise
        and baseline wander that can be removed through filtering.
        """)
        
        fig_raw = create_ecg_plot(
            time_window,
            ecg_window,
            title="Raw ECG Signal"
        )
        st.plotly_chart(fig_raw, use_container_width=True)
    
    # Tab 2: Filtered Signal with Peaks
    with tab2:
        st.subheader("Filtered ECG Signal with R-peak Detection")
        st.markdown(f"""
        The signal has been filtered using a **bandpass filter** ({lowcut}-{highcut} Hz)
        to remove noise and baseline wander. **R-peaks** (marked with ❌) represent
        ventricular depolarization and are used to calculate heart rate.
        """)
        
        # Show comparison plot
        fig_comparison = create_comparison_plot(
            time_window,
            ecg_window,
            ecg_filtered,
            peaks
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Display peak information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Detected Peaks", len(peaks))
        with col2:
            if len(peaks) > 1:
                avg_interval = np.mean(np.diff(peaks)) / fs
                st.metric("Avg RR Interval", f"{avg_interval:.3f} s")
            else:
                st.metric("Avg RR Interval", "N/A")
        with col3:
            st.metric("Time Window", f"{time_range[1] - time_range[0]:.1f} s")
    
    # Tab 3: Heart Rate Analysis
    with tab3:
        st.subheader("Heart Rate Analysis")
        st.markdown("""
        This section shows the **instantaneous heart rate** calculated from the time
        between consecutive R-peaks (RR intervals).
        """)
        
        if len(peaks) >= 2:
            # Create heart rate plot
            fig_hr = create_heart_rate_plot(time_window, peaks, fs)
            st.plotly_chart(fig_hr, use_container_width=True)
            
            # Heart rate statistics
            st.markdown("#### Heart Rate Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean HR", f"{hr_stats['mean_bpm']:.1f} BPM")
            with col2:
                st.metric("Min HR", f"{hr_stats['min_bpm']:.1f} BPM")
            with col3:
                st.metric("Max HR", f"{hr_stats['max_bpm']:.1f} BPM")
            with col4:
                st.metric("Std Dev", f"{hr_stats['std_bpm']:.1f} BPM")
            
            # HRV metrics
            st.markdown("#### Heart Rate Variability (HRV)")
            st.markdown("""
            HRV measures the variation in time between heartbeats and is an indicator
            of autonomic nervous system function.
            """)
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "SDNN",
                    f"{hrv_stats['sdnn']:.1f} ms",
                    help="Standard deviation of RR intervals"
                )
            with col2:
                st.metric(
                    "RMSSD",
                    f"{hrv_stats['rmssd']:.1f} ms",
                    help="Root mean square of successive differences"
                )
        else:
            st.warning("⚠️ Not enough peaks detected to compute heart rate. Try adjusting the detection parameters.")
    
    # Tab 4: Summary Metrics
    with tab4:
        st.subheader("Summary Metrics")
        
        # Data quality metrics
        st.markdown("#### Data Quality")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Signal-to-Noise Ratio", f"{calculate_snr(ecg_filtered):.2f} dB")
        with col2:
            st.metric("Signal Range", f"{np.ptp(ecg_filtered):.3f} mV")
        
        # Detection summary
        st.markdown("#### Detection Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Beats Detected", hr_stats['num_beats'])
        with col2:
            if hr_stats['num_beats'] > 0:
                duration = time_window[-1] - time_window[0]
                st.metric("Average HR (window)", f"{(hr_stats['num_beats'] / duration) * 60:.1f} BPM")
            else:
                st.metric("Average HR (window)", "N/A")
        with col3:
            st.metric("Filter Type", f"Bandpass ({lowcut}-{highcut} Hz)")
        
        # Clinical notes
        st.markdown("#### Clinical Reference")
        st.info("""
        **Normal Resting Heart Rate**: 60-100 BPM  
        **Bradycardia**: < 60 BPM  
        **Tachycardia**: > 100 BPM  
        
        ⚠️ *Note: This tool is for educational purposes only and should not be used for medical diagnosis.*
        """)
        
        # Show raw data option
        if st.checkbox("Show raw data table"):
            data_display = pd.DataFrame({
                'Time (s)': time_window,
                'Raw ECG (mV)': ecg_window,
                'Filtered ECG (mV)': ecg_filtered
            })
            st.dataframe(data_display, use_container_width=True)


def calculate_snr(signal: np.ndarray) -> float:
    """
    Calculate a simple signal-to-noise ratio estimate.
    
    Args:
        signal: Input signal
        
    Returns:
        SNR in decibels
    """
    # Simple SNR estimation using signal power vs. high-frequency noise
    signal_power = np.mean(signal ** 2)
    noise_estimate = np.std(np.diff(signal))
    noise_power = noise_estimate ** 2
    
    if noise_power > 0:
        snr = 10 * np.log10(signal_power / noise_power)
    else:
        snr = float('inf')
    
    return snr


if __name__ == "__main__":
    main()
