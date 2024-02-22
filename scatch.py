import pandas as pd
import matplotlib.pyplot as plt

# Load the data from CSV
file_path = 'data_2024-02-22_14-54-13.csv'  # Update this to the correct path of your CSV file
data = pd.read_csv(file_path)

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(data['Time (ms)'], data['Voltage (mV)'], label='Voltage (mV)')
plt.title('Voltage vs Time')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.legend()
plt.grid(True)
plt.show()
