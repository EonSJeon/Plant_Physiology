import numpy as np
import csv

# Parameters
sampling_rate = 100  # Hz
duration = 60  # seconds
frequency = 1  # Hz, frequency of the sine wave
amplitude = 1  # Amplitude of the sine wave
phase = 0  # Phase shift in radians

# Generate timestamps
timestamps = np.arange(0, duration, 1/sampling_rate)

# Generate sine wave
sine_wave = amplitude * np.sin(2 * np.pi * frequency * timestamps + phase)

# Create CSV file
csv_file = 'sine_wave.csv'
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Value"])  # Header
    for t, value in zip(timestamps, sine_wave):
        writer.writerow([t, value])

print(f"CSV file '{csv_file}' has been generated.")


# import numpy as np
# import csv

# # Parameters
# sampling_rate = 100  # Hz
# duration = 60  # seconds
# pulse_width = 5  # seconds, duration of the rectangular pulse
# pulse_amplitude = 1  # Amplitude of the pulse

# # Generate timestamps
# timestamps = np.arange(0, duration, 1/sampling_rate)

# # Generate rectangular pulse
# # The pulse starts at t=0 and lasts for pulse_width seconds
# rect_pulse = np.zeros_like(timestamps)
# start_index = 0  # Start of the pulse
# end_index = int(pulse_width * sampling_rate)  # End of the pulse
# rect_pulse[start_index:end_index] = pulse_amplitude

# # Create CSV file
# csv_file = 'rect_pulse.csv'
# with open(csv_file, 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(["Timestamp", "Value"])  # Header
#     for t, value in zip(timestamps, rect_pulse):
#         writer.writerow([t, value])

# print(f"CSV file '{csv_file}' has been generated.")
