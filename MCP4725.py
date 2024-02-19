# Author: Sergio Caponi
#
# MCP4725 Digital-to-Analogue converter library for the Virtual Hood Project


__all__ = ['MCP4725']

class MCP4725(object):

	_power_down_mode = {0: 0b00, 
						  1: 0b01, 
						  100: 0b10, 
						  500: 0b11}

	def __init__(self, bus, addr, smbuslib):
		self.bus = bus
		self.addr = addr
		self.smbuslib = smbuslib

	def write(self, value=0, write_to_EEPROM=False, power_down=0):
		if value < 0 or value > 4095:
			raise Exception('Value out of bounds!')

		if power_down not in self._power_down_mode:
			raise Exception('Invalid resistance for power down mode. Supported: 1, 100 and 500 (kOhms)')

		power_down_mode = self._power_down_mode[power_down]

		# Configure the output bits. Device will use fast mode (i.e. transfer in 2 bytes instead of 3)
		# if write_to_EEPROM is false
		if write_to_EEPROM:		# Transfer data in 3 bytes
			config = 0b11
			data = [
				config << 5 | power_down_mode << 1,
				value >> 4,
				value << 4 & 0xFF]		# Use mask to clip the value into an 8-bit int (and remove anything beyond)
		else:					# Transfer data in 2 bytes
			config = 0b00
			data = [
				power_down_mode << 4 | value >> 8,
				value & 0xFF]			# Use mask to clip the value again


		buf = bytes(data)

		# data must be a bytes type of length of 2 or 3
		message = self.smbuslib.i2c_msg.write(self.addr, buf)

		# Write the data onto the device
		self.bus.i2c_rdwr(message)

