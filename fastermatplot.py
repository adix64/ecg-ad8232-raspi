import smbus
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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

# Create figure for plotting
fig, ax = plt.subplots()
xs = []  # Store time
ys = []  # Store ECG signal

# Initialize plot
line, = ax.plot(xs, ys)
plt.title('Real-Time ECG Signal')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    # Read data from the ADS1115
    ecg_value = read_adc()
    
    # Add x and y to lists
    current_time = time.time() - start_time
    xs.append(current_time)
    ys.append(ecg_value)

    # Keep only the last 5 seconds of data
    while xs and xs[0] < current_time - 5:
        xs.pop(0)
        ys.pop(0)

    # Update line with new data
    line.set_xdata(xs)
    line.set_ydata(ys)

    # Adjust the plot limits
    ax.relim()
    ax.autoscale_view()

    return line,

# Initialize start time
start_time = time.time()

# Set up plot to call animate() function periodically with a shorter interval
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=5)  # Reduced interval to 5 ms

# Show the plot
plt.show()
