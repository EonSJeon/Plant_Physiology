from pyftdi.i2c import I2cController

__all__ = ['MCP4725']

class MCP4725(object):
    _power_down_mode = {
        0: 0b00,
        1: 0b01,
        100: 0b10,
        500: 0b11
    }
    __IC_MCP4725_ID = 0x62

    def __init__(self):
        try:
            self.i2c = I2cController()
            self.i2c.configure('ftdi://ftdi:232h/1')  # Adjust the URL as necessary for your FTDI device
        except Exception as e:
            raise IOError(f"Could not initialize I2C device: {e}")

        self.addr = self.__IC_MCP4725_ID

    def write(self, value=0, write_to_EEPROM=False, power_down=0):
        if value < 0 or value > 4095:
            raise Exception('Value out of bounds!')

        if power_down not in self._power_down_mode:
            raise Exception('Invalid resistance for power down mode. Supported: 1, 100, and 500 (kOhms)')

        power_down_mode = self._power_down_mode[power_down]

        if write_to_EEPROM:  # Transfer data in 3 bytes
            config = 0b01100000  # DAC and EEPROM
        else:  # Transfer data in 2 bytes
            config = 0b01000000  # DAC only

        high_byte = config | ((value >> 8) & 0x0F) | (power_down_mode << 1)
        low_byte = value & 0xFF
        data = [high_byte, low_byte] if not write_to_EEPROM else [
            high_byte | (power_down_mode << 4),
            (value >> 4) & 0xFF,
            (value << 4) & 0xFF]

        self._write_i2c(data)

    def _write_i2c(self, data):
        with self.i2c.get_port(self.addr) as port:
            port.write(bytes(data))

