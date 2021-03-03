import array, time
from machine import Pin
import rp2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
    
#delay here is the reset time. You need a pause to reset the LED strip back to the initial LED
#however, if you have quite a bit of processing to do before the next time you update the strip
#you could put in delay=0 (or a lower delay)
class ws2812b:
    def __init__(self, num_leds, state_machine, pin, delay=0.001):
        self.pixels = array.array("I", [0 for _ in range(num_leds)])
        self.sm = rp2.StateMachine(state_machine, ws2812, freq=8000000, sideset_base=Pin(pin))
        self.sm.active(1)
        self.num_leds = num_leds
        self.delay = delay
        self.brightnessvalue = 255

    # Set the overal value to adjust brightness when updating leds
    def brightness(self, brightness = None):
        if brightness == None:
            return self.brightnessvalue
        else:
            if (brightness < 1):
                brightness = 1
        if (brightness > 255):
            brightness = 255
        self.brightnessvalue = brightness

    # Create a gradient with two RGB colors between "pixel1" and "pixel2" (inclusive)
    # Function accepts two (r, g, b) tuples or individual rgb values
    def set_pixel_line_gradient(self, pixel1, pixel2, left_red_or_rgb1, left_green_or_rgb2, left_blue=0, right_red=0, right_green=0, right_blue=0):
        if pixel2 - pixel1 == 0: return
        if type(left_red_or_rgb1) is not tuple:
            left_rgb = (left_red_or_rgb1, left_green_or_rgb2, left_blue)
            right_rgb = (right_red, right_green, right_blue)
        else:
            left_rgb = left_red_or_rgb1
            right_rgb = left_green_or_rgb2
    
        right_pixel = max(pixel1, pixel2)
        left_pixel = min(pixel1, pixel2)
        
        for i in range(right_pixel - left_pixel + 1):
            fraction = i / (right_pixel - left_pixel)
            red = round((right_rgb[0] - left_rgb[0]) * fraction + left_rgb[0])
            green = round((right_rgb[1] - left_rgb[1]) * fraction + left_rgb[1])
            blue = round((right_rgb[2] - left_rgb[2]) * fraction + left_rgb[2])
            
            self.set_pixel(left_pixel + i, (red, green, blue))

    # Set an array of pixels starting from "pixel1" to "pixel2" (inclusive) to the desired color.
    # Function accepts (r, g, b) tuple or individual rgb values
    def set_pixel_line(self, pixel1, pixel2, rgb_or_red, green=0, blue=0):
        if type(rgb_or_red) is not tuple:
            rgb = (rgb_or_red, green, blue)
        else:
            rgb = rgb_or_red

        for i in range(pixel1, pixel2 + 1):
            self.set_pixel(i, rgb)

    # Set red, green and blue value of pixel on position <pixel_num>
    # Function accepts (r, g, b) tuple or individual rgb values
    def set_pixel(self, pixel_num, rgb_or_red, green=0, blue=0):
        if type(rgb_or_red) is not tuple:
            rgb = (rgb_or_red, green, blue)
        else:
            rgb = rgb_or_red

        red = round(rgb[0] * (self.brightness() / 255))
        green = round(rgb[1] * (self.brightness() / 255))
        blue = round(rgb[2] * (self.brightness() / 255))

        self.pixels[pixel_num] = blue | red << 8 | green << 16

    # Rotate <num_of_pixels> pixels to the left
    def rotate_left(self, num_of_pixels):
        if num_of_pixels == None:
            num_of_pixels = 1
        self.pixels = self.pixels[num_of_pixels:] + self.pixels[:num_of_pixels]

    # Rotate <num_of_pixels> pixels to the right
    def rotate_right(self, num_of_pixels):
        if num_of_pixels == None:
            num_of_pixels = 1
        num_of_pixels = -1 * num_of_pixels
        self.pixels = self.pixels[num_of_pixels:] + self.pixels[:num_of_pixels]

    # Update pixels
    def show(self):
        for i in range(self.num_leds):
            self.sm.put(self.pixels[i],8)
        time.sleep(self.delay)

    # Set all pixels to given rgb values
    # Function accepts (r, g, b) tuple or individual rgb values
    def fill(self, rgb_or_red, green=0, blue=0):
        if type(rgb_or_red) is not tuple:
            rgb = (rgb_or_red, green, blue)
        else:
            rgb = rgb_or_red

        for i in range(self.num_leds):
            self.set_pixel(i, rgb)
        time.sleep(self.delay)