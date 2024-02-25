import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load data from CSV
csv_file = 'rect_pulse.csv'
data = pd.read_csv(csv_file)

# Extract signal values and timestamps
timestamps = data['Timestamp'].values
signal = data['Value'].values

# Calculate the sampling rate from the timestamps
# Compute the average difference between successive timestamps to estimate the sampling interval
sampling_interval = np.mean(np.diff(timestamps))
sampling_rate = 1.0 / sampling_interval

# Compute the DTFT (Discrete Fourier Transform)
signal_fft = np.fft.fft(signal)

# Compute the frequencies for each FFT output component
n = signal.size
freq = np.fft.fftfreq(n, d=sampling_interval)

# Create subplots
fig, axs = plt.subplots(2, 1, figsize=(12, 10))

# Plot in the time domain
axs[0].plot(timestamps, signal, label='Original Signal')
axs[0].set_title('Time Domain Signal')
axs[0].set_xlabel('Time (seconds)')
axs[0].set_ylabel('Amplitude')
axs[0].grid(True)

# Plot the magnitude of the DTFT (FFT) in the frequency domain
axs[1].plot(freq, np.abs(signal_fft))
axs[1].set_title('Magnitude of DTFT of the Signal')
axs[1].set_xlabel('Frequency (Hz)')
axs[1].set_ylabel('Magnitude')
axs[1].grid(True)
# Limit the x-axis to visualize the meaningful part of the spectrum
axs[1].set_xlim([0, sampling_rate / 2])

plt.tight_layout()
plt.show()
