from pyftdi.i2c import I2cController

# Create an instance of the I2C controller
i2c = I2cController()

try:
    # Configure the FTDI device
    # Replace 'ftdi://ftdi:232h/1' with the appropriate URL for your device
    i2c.configure('ftdi://ftdi:232h/1')

    # Replace 'your_device_address' with the I2C address of your device
    # The I2C address should be shifted left (<< 1) as pyftdi expects a 8-bit address
    device_address = 0x40  # Example device address
    i2c_device = i2c.get_port(device_address)

    # Example write operation: Write a byte array to the device
    data_to_write = bytearray([0x00, 0x01, 0x02])  # Example data
    i2c_device.write(data_to_write)

    # Example read operation: Read a byte array from the device
    number_of_bytes_to_read = 3  # Example: read 3 bytes
    read_data = i2c_device.read(number_of_bytes_to_read)
    print(f"Read data: {read_data}")

finally:
    # Ensure the I2C controller is properly terminated
    i2c.terminate()
