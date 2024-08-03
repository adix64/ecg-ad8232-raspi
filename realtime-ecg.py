import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# Pin setup
ECG_PIN = 18  # The GPIO pin connected to the AD8232 OUTPUT

GPIO.setmode(GPIO.BCM)
GPIO.setup(ECG_PIN, GPIO.IN)

# Create figure for plotting
fig, ax = plt.subplots()
xs = []  # Store time
ys = []  # Store ECG signal

# Initialize plot
line, = ax.plot(xs, ys)
plt.title('Real-Time ECG Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    # Read data from the GPIO pin
    ecg_value = GPIO.input(ECG_PIN)
    
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

# Clean up GPIO on exit
GPIO.cleanup()
