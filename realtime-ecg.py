import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS object
ads = ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS1115.P0)

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
    ecg_value = chan.voltage
    
    # Add x and y to lists
    current_time = time.time() - start_time
    xs.append(current_time)
    ys.append(ecg_value)

    # Limit x and y lists to 200 items
    xs = xs[-200:]
    ys = ys[-200:]

    # Update line with new data
    line.set_xdata(xs)
    line.set_ydata(ys)

    # Adjust the plot limits
    ax.relim()
    ax.autoscale_view()

    return line,

# Initialize start time
start_time = time.time()

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=10)

# Show the plot
plt.show()
