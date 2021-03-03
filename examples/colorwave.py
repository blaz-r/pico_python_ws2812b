# Example showing how functions, that accept tuples of rgb values,
# simplify working with gradients

import time
import ws2812b

numpix = 60
strip = ws2812b.ws2812b(numpix, 0, 0)

red = (255, 0, 0)
orange = (255, 50, 0)
yellow = (255, 100, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (100, 0, 90)
violet = (200, 0, 100)
colors = [red, orange, yellow, green, blue, indigo, violet]

step = round(numpix / len(colors))
current_pixel = 0
strip.brightness(20)

for color1, color2 in zip(colors, colors[1:]):
    strip.set_pixel_line_gradient(current_pixel, current_pixel + step, color1, color2)
    current_pixel += step

strip.set_pixel_line_gradient(current_pixel, numpix - 1, violet, red)

while True:
    strip.rotate_right(1)
    time.sleep(0.042)
    strip.show()
