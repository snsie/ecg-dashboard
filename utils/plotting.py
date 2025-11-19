"""Plotting utilities for ECG visualization."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Optional


def create_ecg_plot(
    time: np.ndarray,
    ecg_signal: np.ndarray,
    title: str = "ECG Signal",
    peaks: Optional[np.ndarray] = None,
    peak_label: str = "R-peaks"
) -> go.Figure:
    """
    Create an interactive plotly figure for ECG signal visualization.
    
    Args:
        time: Time array in seconds
        ecg_signal: ECG signal values
        title: Plot title
        peaks: Optional array of peak indices
        peak_label: Label for peaks
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add ECG trace
    fig.add_trace(go.Scatter(
        x=time,
        y=ecg_signal,
        mode='lines',
        name='ECG',
        line=dict(color='#2E86AB', width=1.5),
        hovertemplate='Time: %{x:.3f}s<br>Amplitude: %{y:.3f}<extra></extra>'
    ))
    
    # Add peaks if provided
    if peaks is not None and len(peaks) > 0:
        fig.add_trace(go.Scatter(
            x=time[peaks],
            y=ecg_signal[peaks],
            mode='markers',
            name=peak_label,
            marker=dict(
                color='#E63946',
                size=10,
                symbol='x',
                line=dict(width=2)
            ),
            hovertemplate='Peak at: %{x:.3f}s<br>Amplitude: %{y:.3f}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude (mV)",
        hovermode='closest',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_comparison_plot(
    time: np.ndarray,
    raw_signal: np.ndarray,
    filtered_signal: np.ndarray,
    peaks: Optional[np.ndarray] = None
) -> go.Figure:
    """
    Create a comparison plot showing raw and filtered signals.
    
    Args:
        time: Time array in seconds
        raw_signal: Raw ECG signal
        filtered_signal: Filtered ECG signal
        peaks: Optional array of peak indices
        
    Returns:
        Plotly figure object with subplots
    """
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Raw ECG Signal', 'Filtered ECG Signal with Detected R-peaks'),
        vertical_spacing=0.12
    )
    
    # Raw signal
    fig.add_trace(
        go.Scatter(
            x=time,
            y=raw_signal,
            mode='lines',
            name='Raw ECG',
            line=dict(color='#A8DADC', width=1.5),
            hovertemplate='Time: %{x:.3f}s<br>Amplitude: %{y:.3f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Filtered signal
    fig.add_trace(
        go.Scatter(
            x=time,
            y=filtered_signal,
            mode='lines',
            name='Filtered ECG',
            line=dict(color='#2E86AB', width=1.5),
            hovertemplate='Time: %{x:.3f}s<br>Amplitude: %{y:.3f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Add peaks to filtered signal
    if peaks is not None and len(peaks) > 0:
        fig.add_trace(
            go.Scatter(
                x=time[peaks],
                y=filtered_signal[peaks],
                mode='markers',
                name='R-peaks',
                marker=dict(
                    color='#E63946',
                    size=10,
                    symbol='x',
                    line=dict(width=2)
                ),
                hovertemplate='Peak at: %{x:.3f}s<br>Amplitude: %{y:.3f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_xaxes(title_text="Time (seconds)", row=2, col=1)
    fig.update_yaxes(title_text="Amplitude (mV)", row=1, col=1)
    fig.update_yaxes(title_text="Amplitude (mV)", row=2, col=1)
    
    fig.update_layout(
        height=800,
        showlegend=True,
        template='plotly_white',
        hovermode='closest'
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_heart_rate_plot(
    time: np.ndarray,
    peak_indices: np.ndarray,
    fs: float
) -> go.Figure:
    """
    Create a plot showing instantaneous heart rate over time.
    
    Args:
        time: Time array in seconds
        peak_indices: Array of R-peak indices
        fs: Sampling frequency in Hz
        
    Returns:
        Plotly figure object
    """
    if len(peak_indices) < 2:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough peaks detected to compute heart rate",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Calculate RR intervals and instantaneous HR
    rr_intervals = np.diff(peak_indices) / fs
    instantaneous_hr = 60.0 / rr_intervals
    hr_times = time[peak_indices[1:]]  # Time points for each HR value
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hr_times,
        y=instantaneous_hr,
        mode='lines+markers',
        name='Heart Rate',
        line=dict(color='#E63946', width=2),
        marker=dict(size=8),
        hovertemplate='Time: %{x:.3f}s<br>HR: %{y:.1f} BPM<extra></extra>'
    ))
    
    # Add mean line
    mean_hr = np.mean(instantaneous_hr)
    fig.add_hline(
        y=mean_hr,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Mean: {mean_hr:.1f} BPM",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=dict(text="Instantaneous Heart Rate", x=0.5, xanchor='center'),
        xaxis_title="Time (seconds)",
        yaxis_title="Heart Rate (BPM)",
        hovermode='closest',
        template='plotly_white',
        height=400
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig
