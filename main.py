from pyftdi.i2c import I2cController

# Create an I2C controller instance
i2c = I2cController()

# Configure the I2C interface with the FT232H device
# Replace 'ftdi://ftdi:232h/1' with the appropriate device string for your setup
i2c.configure('ftdi://ftdi:232h/1')

try:
    # Open a connection to the I2C slave device at address 0x40
    # Replace 0x40 with the address of your device
    slave = i2c.get_port(0x40)
    
    # Example: Read 2 bytes from register 0x01 of the device
    # Adjust the register and byte count as necessary for your device
    register_address = 0x01
    data = slave.read_from(register_address, 2)
    print(f"Data read from device: {data}")
    
    # Example: Write a byte to register 0x02 of the device
    # Replace the register address and data as needed for your device
    slave.write_to(0x02, b'\x01')  # Writing 0x01 to register 0x02
    print("Write operation completed")
    
finally:
    # Make sure to deinitialize the controller
    i2c.terminate()
