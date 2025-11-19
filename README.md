# ECG Signal Analysis Dashboard

An interactive biomedical data visualization and analysis application for Electrocardiogram (ECG) signals built with Streamlit.

## Biomedical Context

An **Electrocardiogram (ECG or EKG)** is a medical test that measures the electrical activity of the heart over time. Each heartbeat produces electrical signals that trigger the heart muscle to contract and pump blood. ECG signals are crucial for:

- **Detecting cardiac arrhythmias** and irregular heartbeats
- **Monitoring heart rate** and rhythm patterns
- **Diagnosing heart conditions** such as heart attacks, coronary artery disease, and electrolyte imbalances
- **Assessing heart rate variability (HRV)** as an indicator of autonomic nervous system function

This application allows users to visualize ECG signals, apply signal processing techniques (filtering), detect R-peaks (the prominent peaks in the QRS complex representing ventricular depolarization), and calculate heart rate metrics.

## Quick Start Instructions

### Opening the Repository in GitHub Codespaces

1. Navigate to the repository on GitHub: `https://github.com/snsie/ecg-dashboard`
2. Click the **Code** button (green button)
3. Select the **Codespaces** tab
4. Click **Create codespace on main** (or your current branch)
5. Wait for the Codespace to initialize (this may take a minute)

### Running the Application

Once your Codespace is ready, follow these steps in the integrated terminal:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
```

After running the command, Streamlit will provide a **Local URL** (usually `http://localhost:8501`). In GitHub Codespaces:
- A popup will appear asking if you want to open the application
- Click **Open in Browser** to view the dashboard
- Alternatively, go to the **Ports** tab in VS Code and click on the forwarded port

## Usage Guide

### Step 1: Start the Application
After running `streamlit run streamlit_app.py`, the application will open in your browser showing the ECG Dashboard with four main tabs.

### Step 2: Configure Analysis Parameters
Use the **Control Panel** in the left sidebar to adjust:

- **Time Window Selection**: Choose which portion of the signal to analyze using the slider
- **Filter Parameters**: 
  - Low cutoff frequency (0.1-5 Hz) - removes baseline wander
  - High cutoff frequency (10-100 Hz) - removes high-frequency noise
- **Peak Detection**:
  - Peak detection threshold (0.1-0.9) - sensitivity for detecting R-peaks
  - Minimum peak distance (0.2-1.0 seconds) - prevents detecting multiple peaks too close together

### Step 3: Explore the Visualizations

Navigate through the tabs:

- **📈 Raw Signal**: View the unprocessed ECG signal as loaded from the data file
- **🔬 Filtered Signal & Peaks**: See the bandpass-filtered signal with detected R-peaks marked
- **💓 Heart Rate Analysis**: View instantaneous heart rate over time with statistics
- **📊 Summary Metrics**: Review comprehensive metrics including signal quality, detection summary, and clinical reference values

### Step 4: Interpret the Results

The application provides:
- **Heart Rate Statistics**: Mean, min, max, and standard deviation of heart rate in BPM
- **HRV Metrics**: SDNN and RMSSD values indicating heart rate variability
- **Clinical Context**: Normal ranges and interpretation guidelines

### Step 5: Adjust Parameters for Better Detection

If peaks are not being detected correctly:
- Increase the **threshold** if too many false peaks are detected
- Decrease the **threshold** if R-peaks are being missed
- Adjust **minimum peak distance** based on the expected heart rate (lower for faster rates)
- Modify **filter cutoff frequencies** to improve signal quality

## Data Description

### Data Source

This application uses **synthetic ECG data** generated programmatically to simulate realistic ECG signals. The synthetic data is created when you first run the application and is saved to `data/sample_ecg.csv`.

**Synthetic Signal Characteristics:**
- **Duration**: 30 seconds
- **Sampling Rate**: 360 Hz (360 samples per second)
- **Heart Rate**: Approximately 72 BPM (beats per minute)
- **Components**: Includes P-wave, QRS complex, and T-wave morphology typical of normal sinus rhythm
- **Artifacts**: Contains simulated baseline wander and noise to make it realistic

The synthetic data is automatically generated on first run if the file doesn't exist, ensuring the app always works out of the box.

### Using Your Own Data

To use your own ECG data:
1. Format your data as a CSV file with two columns: `time` (in seconds) and `ecg` (signal amplitude in mV)
2. Replace the file `data/sample_ecg.csv` with your data
3. Restart the application

## Project Structure

```
ecg-dashboard/
├── streamlit_app.py          # Main Streamlit application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── data/
│   └── sample_ecg.csv        # Synthetic ECG data (generated on first run)
└── utils/
    ├── __init__.py           # Package initialization
    ├── data_loader.py        # Functions for loading and generating ECG data
    ├── signal_processing.py  # Signal filtering, peak detection, HR calculation
    └── plotting.py           # Plotly visualization functions
```

### Key Files

- **`streamlit_app.py`**: The main application file containing the Streamlit UI layout, user controls, and orchestration of data processing and visualization.

- **`utils/data_loader.py`**: Contains functions for:
  - Loading ECG data from CSV files
  - Generating synthetic ECG signals with realistic morphology
  - Saving synthetic data to disk

- **`utils/signal_processing.py`**: Implements core signal processing algorithms:
  - Butterworth bandpass filtering
  - R-peak detection using `scipy.signal.find_peaks`
  - Heart rate and HRV calculations

- **`utils/plotting.py`**: Helper functions that create interactive Plotly visualizations:
  - ECG signal plots with optional peak markers
  - Comparison plots (raw vs. filtered)
  - Heart rate over time plots

## Features

✅ **Interactive Signal Visualization**: Zoom, pan, and select time windows  
✅ **Bandpass Filtering**: Remove noise and baseline wander with adjustable cutoffs  
✅ **R-Peak Detection**: Automatic detection of heartbeats with configurable sensitivity  
✅ **Heart Rate Calculation**: Compute mean, min, max heart rate in BPM  
✅ **HRV Analysis**: Calculate SDNN and RMSSD metrics  
✅ **User-Friendly Interface**: Intuitive controls with helpful tooltips  
✅ **Educational Context**: Clinical reference values and explanations  

## Technical Details

**Libraries Used:**
- `streamlit` - Web application framework
- `numpy` - Numerical computations
- `pandas` - Data manipulation
- `scipy` - Signal processing algorithms (filtering, peak detection)
- `plotly` - Interactive visualizations

**Signal Processing Pipeline:**
1. Load raw ECG data
2. Select time window of interest
3. Apply Butterworth bandpass filter (default: 0.5-40 Hz)
4. Detect R-peaks using threshold-based algorithm
5. Calculate RR intervals from peak positions
6. Compute heart rate and HRV metrics

## Notes

⚠️ **Educational Use Only**: This application is designed for educational and demonstration purposes. It should **not** be used for medical diagnosis or clinical decision-making. Always consult qualified healthcare professionals for medical advice.

## License

This project is open source and available for educational purposes.
