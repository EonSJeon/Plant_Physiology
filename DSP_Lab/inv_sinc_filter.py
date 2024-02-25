import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

HPBW_CONST=0.44295*2

def geometric_space(sp, ep, n=10, r=0.5):
    L = ep - sp
    a = L * (1 - r) / (1 - r**n)
    powers_of_r = np.arange(n)
    geometric_progression = a * r**powers_of_r
    pts = np.cumsum(geometric_progression)
    pts = np.insert(pts, 0, sp)
    pts[-1] = ep  
    return pts

def nullify_0th_ord_interp(data):
    time_step=(data[-1][0]-data[0][0])/data.shape[0]
    hpbw=(2*HPBW_CONST)/(time_step*np.pi)
    cutoff=hpbw/2
    fs=1/time_step
    
    n=10
    start_edges = geometric_space(0, cutoff, n, 0.5)
    end_edges = start_edges[:-1] + (start_edges[1:] - start_edges[:-1]) * 0.2
    start_edges = start_edges[:-1]  # Exclude the last start edge, as it has no corresponding end edge
    
    band_edges = np.column_stack((start_edges, end_edges))
    
    bands = np.append(band_edges.flatten(), [cutoff, fs/2])
    desired = np.append(1/(2*time_step*np.sinc(time_step*np.pi*start_edges)),0)
    weights = np.append(np.logspace(1, 3, num=n-1,base=10),1)
    
    taps =signal.remez(101, bands, desired, weight=weights, fs=fs, maxiter=1000)



# Read the data from CSV
fileName = 'sine_wave.csv'
data = np.genfromtxt(fileName, delimiter=',', skip_header=1)

# Extract timestamps and values
timestamps = data[:,0]
values = data[:,1]

# Upsample configuration
upsample_factor = 5  # Define the upsampling factor

# Perform 0th order hold interpolation (nearest-neighbor)
upsampled_time = np.arange(timestamps[0], timestamps[-1], (timestamps[1] - timestamps[0]) / upsample_factor)
upsampled_values = np.repeat(values, upsample_factor)[:len(upsampled_time)]

# Low-pass filter configuration
cutoff_frequency = 1.0  # Adjust the cutoff frequency as needed
nyquist_rate = 0.5 * upsample_factor / (timestamps[1] - timestamps[0])
normalized_cutoff = cutoff_frequency / nyquist_rate

# Design a low-pass FIR filter
numtaps = 101  # Number of taps in the FIR filter, can be adjusted for the filter response
fir_coeff = signal.firwin(numtaps, normalized_cutoff)

# Apply the filter
filtered_values = signal.lfilter(fir_coeff, 1.0, upsampled_values)

# Plot the original and processed signals for comparison
plt.figure(figsize=(10, 6))
plt.plot(timestamps, values, label='Original Signal')
plt.plot(upsampled_time, upsampled_values, label='Upsampled Signal', alpha=0.5)
plt.plot(upsampled_time, filtered_values, label='Filtered Signal', linestyle='--')
plt.legend()
plt.xlabel('Timestamp')
plt.ylabel('Value')
plt.title('Signal Processing: Upsampling and Low-pass Filtering')
plt.show()



####################################################################################
# # Design parameters
# fs = 100  # Sampling frequency (Hz)
# N = 101  # Filter order
# cutoff = 40  # Cutoff frequency for the approximation (Hz)

# # Generate frequency points for the desired approximation
# freq_points = np.linspace(0, fs / 2, 400)
# freq_points[0] = 1e-6  # Avoid division by zero at DC

# # Calculate the desired approximate 1/sinc(f) response
# desired_response = 1 / np.sinc(2 * freq_points / fs)

# # Define finer bands for filter design
# # Splitting the frequency range into finer bands allows for a closer approximation
# band_edges = np.linspace(0, cutoff, 10)  # More bands up to the cutoff frequency
# band_edges1 = np.repeat(band_edges, 2)
# band_edges1 = band_edges1[1:-2]
# # Adjust every other element starting from the second duplicated element
# for i in range(1, len(band_edges1), 2):
#     band_edges1[i] -= 1  # Increment to create a small gap between bands



# band_edges1 = np.append(band_edges1, [cutoff, cutoff + 5, fs / 2])  # Append stop band edges


# print(band_edges1)

# # Desired gains for each band, calculated at band edges
# desired_gains = 1 / np.sinc(2 * band_edges / fs)

# # Since remez cannot directly use a continuous desired response, approximate by setting gains at band edges
# bands = band_edges1
# desired = desired_gains
# desired[-1]=0

# # Weights - emphasize the passband more
# weights = np.ones_like(band_edges)*100
# weights[-1] = 1  # Increase weight for the passband


# print(len(bands))
# print(len(desired))
# print(len(weights))
# print(weights)

# # Design the filter using the remez algorithm
# taps = signal.remez(N, bands, desired, weight=weights, fs=fs, maxiter=1000)

# # Frequency response of the designed filter
# w, h = signal.freqz(taps, worN=8000, fs=fs)
# plt.figure(figsize=(14, 15))

# # Plot 1: Logarithmic scale (decibels) for magnitude
# plt.subplot(3, 1, 1)
# plt.plot(freq_points, 20 * np.log10(desired_response), label='Desired Approximate 1/sinc(f)', linestyle='--')
# plt.plot(w, 20 * np.log10(abs(h)), label='Designed Filter Response')
# plt.title('Approximate 1/sinc(f) Compensation Filter Response (Log Scale)')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Gain (dB)')
# plt.legend()
# plt.grid()

# # Plot 2: Linear scale for magnitude
# plt.subplot(3, 1, 2)
# plt.plot(freq_points, desired_response, label='Desired Approximate 1/sinc(f)', linestyle='--', alpha=0.7)
# plt.plot(w, abs(h), label='Designed Filter Response', alpha=0.7)
# plt.title('Approximate 1/sinc(f) Compensation Filter Response (Linear Scale)')

# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Gain')
# plt.ylim([0, 100])
# plt.legend()
# plt.grid()

# # Plot 3: Phase response
# plt.subplot(3, 1, 3)
# phase_response = np.angle(h)  # Calculate phase response
# plt.plot(w, phase_response, label='Phase Response', color='green')
# plt.title('Phase Response of the Designed Filter')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Phase (radians)')
# plt.legend()
# plt.grid()

# plt.tight_layout()  # Adjust layout to not overlap subplots
# plt.show()