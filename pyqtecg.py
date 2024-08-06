import sys
import time
import smbus
from PyQt5 import QtWidgets
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

# Define I2C bus and address
I2C_BUS = 1  # For Raspberry Pi 3 and later
ADS1115_ADDRESS = 0x48  # Default I2C address for ADS1115

# Define ADS1115 registers
ADS1115_POINTER_CONVERSION = 0x00
ADS1115_POINTER_CONFIG = 0x01

# Define configuration register options
ADS1115_CONFIG_OS_SINGLE = 0x8000
ADS1115_CONFIG_MUX_SINGLE_0 = 0x4000
ADS1115_CONFIG_PGA_6_144V = 0x0200
ADS1115_CONFIG_MODE_SINGLE = 0x0100
ADS1115_CONFIG_DR_860SPS = 0x00E0  # Increased sample rate to 860 SPS
ADS1115_CONFIG_COMP_QUE_DISABLE = 0x0003

# Create SMBus instance
bus = smbus.SMBus(I2C_BUS)

def read_adc():
    # Configure ADS1115
    config = (
        ADS1115_CONFIG_OS_SINGLE |
        ADS1115_CONFIG_MUX_SINGLE_0 |
        ADS1115_CONFIG_PGA_6_144V |
        ADS1115_CONFIG_MODE_SINGLE |
        ADS1115_CONFIG_DR_860SPS |  # Increased sample rate to 860 SPS
        ADS1115_CONFIG_COMP_QUE_DISABLE
    )
    
    # Write config register
    bus.write_i2c_block_data(ADS1115_ADDRESS, ADS1115_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
    
    # Wait for conversion to complete
    time.sleep(1.0 / 860)  # Reduced wait time for higher sample rate
    
    # Read conversion result
    result = bus.read_i2c_block_data(ADS1115_ADDRESS, ADS1115_POINTER_CONVERSION, 2)
    raw_adc = (result[0] << 8) | result[1]
    
    # Convert to signed value
    if raw_adc > 0x7FFF:
        raw_adc -= 0x10000
        
    # Convert to voltage
    voltage = raw_adc * 6.144 / 32768.0
    return voltage

class ECGPlot:
    def __init__(self):
        # Create a Qt application
        self.app = QtWidgets.QApplication(sys.argv)

        # Create a window with a plot
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.win.setWindowTitle('Real-Time ECG Signal')
        self.plot = self.win.addPlot()
        self.plot.setLabel('bottom', 'Time', 's')
        self.plot.setLabel('left', 'Voltage', 'V')

        # Create lists to store time and voltage data
        self.xs = []
        self.ys = []

        # Create a curve to update
        self.curve = self.plot.plot(self.xs, self.ys, pen='y')

        # Initialize a timer to update the plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)  # Update every 10 ms

        # Initialize start time
        self.start_time = time.time()

    def update(self):
        # Read data from the ADS1115
        ecg_value = read_adc()

        # Add x and y to lists
        current_time = time.time() - self.start_time
        self.xs.append(current_time)
        self.ys.append(ecg_value)

        # Keep only the last 5 seconds of data
        while self.xs and self.xs[0] < current_time - 5:
            self.xs.pop(0)
            self.ys.pop(0)

        # Update the curve with the new data
        self.curve.setData(self.xs, self.ys)

    def run(self):
        QtGui.QApplication.instance().exec_()

if __name__ == '__main__':
    ecg_plot = ECGPlot()
    ecg_plot.run()
