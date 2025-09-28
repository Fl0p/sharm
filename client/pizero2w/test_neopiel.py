import time
import pigpio
from rpi_ws281x import PixelStrip, Color

LED_COUNT      = 7
LED_PIN        = 12
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 64
LED_INVERT     = False
LED_CHANNEL    = 0

# Initialize pigpio (keep usage), but do not pass 'pi' into PixelStrip
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon is not running. Start it with 'sudo systemctl start pigpiod'")

# Initialize LED strip using rpi_ws281x without pigpio argument
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                   LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                   strip_type=None)
strip.begin()

def color_wipe(color, wait_ms=200):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

try:
    while True:
        color_wipe(Color(255, 0, 0))
        time.sleep(0.5)
        color_wipe(Color(0, 255, 0))
        time.sleep(0.5)
        color_wipe(Color(0, 0, 255))
        time.sleep(0.5)
except KeyboardInterrupt:
    color_wipe(Color(0, 0, 0), 50)
    pi.stop()
