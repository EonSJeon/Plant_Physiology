import time
from pyftdi.i2c import I2cController

__all__ = ['ADS1115']

class ADS1115:
    i2c = None

    # IC Identifiers
    __IC_ADS1115 = 0x01
    
    # Address mode
    __ADS1015_GND_ADR = 0b1001000
    __ADS1015_VDD_ADR = 0b1001001
    __ADS1015_SDA_ADR = 0b1001010
    __ADS1015_SCL_ADR = 0b1001011

    # Config Register
    __ADS1115_REG_CONFIG_DR_8SPS      = 0x0000  # 8 samples per second
    __ADS1115_REG_CONFIG_DR_16SPS     = 0x0020  # 16 samples per second
    __ADS1115_REG_CONFIG_DR_32SPS     = 0x0040  # 32 samples per second
    __ADS1115_REG_CONFIG_DR_64SPS     = 0x0060  # 64 samples per second
    __ADS1115_REG_CONFIG_DR_128SPS    = 0x0080  # 128 samples per second
    __ADS1115_REG_CONFIG_DR_250SPS    = 0x00A0  # 250 samples per second (default)
    __ADS1115_REG_CONFIG_DR_475SPS    = 0x00C0  # 475 samples per second
    __ADS1115_REG_CONFIG_DR_860SPS    = 0x00E0  # 860 samples per second

    __ADS1015_REG_CONFIG_CQUE_MASK    = 0x0003
    __ADS1015_REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
    __ADS1015_REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
    __ADS1015_REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
    __ADS1015_REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

    __ADS1015_REG_CONFIG_CMODE_MASK   = 0x0010
    __ADS1015_REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis (default)
    __ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

    __ADS1015_REG_CONFIG_CPOL_MASK    = 0x0008
    __ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active (default)
    __ADS1015_REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

    __ADS1015_REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
    __ADS1015_REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator (default)
    __ADS1015_REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

    __ADS1015_REG_CONFIG_MODE_MASK    = 0x0100
    __ADS1015_REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
    __ADS1015_REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default)

    __ADS1015_REG_CONFIG_PGA_MASK     = 0x0E00
    __ADS1015_REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range
    __ADS1015_REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range
    __ADS1015_REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range (default)
    __ADS1015_REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range
    __ADS1015_REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range
    __ADS1015_REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range

    __ADS1015_REG_CONFIG_MUX_MASK     = 0x7000
    __ADS1015_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 (default)
    __ADS1015_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    __ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    __ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    __ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    __ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

     # Config Register
    __ADS1015_REG_CONFIG_OS_MASK      = 0x8000
    __ADS1015_REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
    __ADS1015_REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit = 0 when conversion is in progress
    __ADS1015_REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit = 1 when device is not performing a conversion

    # Pointer Register
    __ADS1015_REG_POINTER_MASK        = 0x03
    __ADS1015_REG_POINTER_CONVERT     = 0x00
    __ADS1015_REG_POINTER_CONFIG      = 0x01
    __ADS1015_REG_POINTER_LOWTHRESH   = 0x02
    __ADS1015_REG_POINTER_HITHRESH    = 0x03
    
    # Dictionaries with the sampling speed values
    # These simplify and clean the code (avoid the abuse of if/elif/else clauses)
    spsADS1115 = {
        8:__ADS1115_REG_CONFIG_DR_8SPS,
        16:__ADS1115_REG_CONFIG_DR_16SPS,
        32:__ADS1115_REG_CONFIG_DR_32SPS,
        64:__ADS1115_REG_CONFIG_DR_64SPS,
        128:__ADS1115_REG_CONFIG_DR_128SPS,
        250:__ADS1115_REG_CONFIG_DR_250SPS,
        475:__ADS1115_REG_CONFIG_DR_475SPS,
        860:__ADS1115_REG_CONFIG_DR_860SPS
        }   

    # Dictionariy with the programable gains
    pgaADS1x15 = {
        6144:__ADS1015_REG_CONFIG_PGA_6_144V,
        4096:__ADS1015_REG_CONFIG_PGA_4_096V,
        2048:__ADS1015_REG_CONFIG_PGA_2_048V,
        1024:__ADS1015_REG_CONFIG_PGA_1_024V,
        512:__ADS1015_REG_CONFIG_PGA_0_512V,
        256:__ADS1015_REG_CONFIG_PGA_0_256V
        }  

   # Constructor
    def __init__(self):
        try:
            self.i2c = I2cController()
            self.i2c.configure('ftdi://ftdi:232h/1')  # Example URL, adjust as needed
        except Exception as e:
            raise IOError(f"Could not initialize I2C device: {e}")
        self.ic = self.__IC_ADS1115
        self.address = self.__ADS1015_GND_ADR

        self.pga = 0
        self.sps = 0

    def write_i2c(self, register, data):
        i2c_port = self.i2c.get_port(self.address)
        i2c_port.write_to(register, data)

    def read_i2c(self, register, length):
        i2c_port = self.i2c.get_port(self.address)
        return i2c_port.read_from(register, length)

    def setADCConfig(self, mux=__ADS1015_REG_CONFIG_MUX_SINGLE_0,sps=860, pga=6144):
        self.sps=sps
        self.pga=pga
        config = self.__ADS1015_REG_CONFIG_CQUE_NONE    | \
                 self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                 self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                 self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                 self.__ADS1015_REG_CONFIG_MODE_CONTIN  | \
                 self.__ADS1015_REG_CONFIG_OS_SINGLE    | \
                 mux | self.spsADS1115[sps] | self.pgaADS1x15[pga]
        
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        self.write_i2c(self.__ADS1015_REG_POINTER_CONFIG, bytes)
    
    def read(self):
        # delay = 1.0/self.sps+0.0001
        # time.sleep(delay)

        result = self.read_i2c(self.__ADS1015_REG_POINTER_CONVERT, 2)

        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            return (val - 0xFFFF)*self.pga/32768.0
        else:
            return ( (result[0] << 8) | (result[1]) )*self.pga/32768.0         


    def readADCSingleEnded(self, channel=0, pga=6144, sps=860):
        ''' 
            Gets a single-ended ADC reading from the specified channel in mV. 
            The sample rate for this mode (single-shot) can be used to lower the noise 
            (low sps) or to lower the power consumption (high sps) by duty cycling, 
            see datasheet page 14 for more info. 
            The pga must be given in mV, see page 13 for the supported values. 
        '''
    
        # With invalid channel return -1
        if (channel > 3):
            return -1
    
        # Disable comparator, Non-latching, Alert/Rdy active low
        # traditional comparator, single-shot mode
        config = self.__ADS1015_REG_CONFIG_CQUE_NONE    | \
                 self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                 self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                 self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                 self.__ADS1015_REG_CONFIG_MODE_CONTIN

        # Set sample per seconds, defaults to 250sps
        config |= self.spsADS1115.setdefault(sps, self.__ADS1115_REG_CONFIG_DR_860SPS)

        # Set PGA/voltage range, defaults to +-6.144V  
        config |= self.pgaADS1x15.setdefault(pga, self.__ADS1015_REG_CONFIG_PGA_6_144V)
        self.pga = pga

        # Set the channel to be converted
        if channel == 3:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_3
        elif channel == 2:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_2
        elif channel == 1:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_1
        else:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_0

        # Set 'start single-conversion' bit
        config |= self.__ADS1015_REG_CONFIG_OS_SINGLE

        # Write config register to the ADC
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        self.write_i2c(self.address, self.__ADS1015_REG_POINTER_CONFIG, bytes)

        # Wait for the ADC conversion to complete
        # The minimum delay depends on the sps: delay >= 1/sps
        # We add 0.1ms to be sure
        delay = 1.0/sps+0.0001
        time.sleep(delay)

        # Read the conversion results
        result = self.read_i2c(self.address, self.__ADS1015_REG_POINTER_CONVERT, 2)
        # Return a mV value for the ADS1115
        # (Take signed values into account as well)
        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            return (val - 0xFFFF)*pga/32768.0
        else:
            return ( (result[0] << 8) | (result[1]) )*pga/32768.0
