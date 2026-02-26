# PROG 5120 - AI Programming ASSIGN 2 - Mike Lalonde
# Question 1 - Mandelbrot 
#  Project reference - TUTORIAL -  https://realpython.com/mandelbrot-set-python/#plotting-the-mandelbrot-set-using-pythons-matplotlib
#  PIL Docs - https://pillow.readthedocs.io/en/stable/

# Part One - The Mandelbrot set is a mathematical set of complex numbers that tests how each point
# behaves when we repeatedly apply the rule z -> z**2 + c. This formula is applied to every pixel
# on the computer screen. The iteration always starts with z = 0. As we keep applying the rule, we
# check whether z stays bounded or whether it blows up to infinity. Points where z stays bounded
# are inside the Mandelbrot set. Points where z escapes are outside it. When the results are plotted,
# they create an intricate, infinitely repeating fractal pattern.

# A complex number can be thought of as similar to a 2D vector, but with a special rule of
# multiplication that rotates, scales, and flips the vector. This special behavior is what
# creates the fractal patterns when z is squared repeatedly.

# A complex number is written as z = x + yi, where x is the real part, y is the imaginary part,
# and i is the imaginary unit (with i**2 = -1).

# PSUEDO code

# CREATE a MandelbrotSet object 
# CREATE a new empty 512 x 512 RGB image
# SETUP a Viewport over this image with:
# FOR EACH pixel IN the Viewport:
#     CONVERT the pixel position into a complex number c
#     check the stability of c:
#         stability = mandelbrot_set.stability(c, smooth = true)
#     IF stability == 1 THEN
#         SET pixel color to black  (0, 0, 0)
#     ELSE
#         CALCULATE a color based on stability using HSB
#         SET pixel color to that HSB color
# SHOW the image on the screen

# CODE inspired by Tutorial code....some changes but minor.  
# Brought Mandlebrot class into code from mandelbrot_03
# changed viewport to be larger
# commented code for readability
# played with iterations and escape radius.

from PIL import Image
from PIL.ImageColor import getrgb
from viewport import Viewport  
import math


class MandelbrotSet:
    """
    Represents the Mandelbrot set and lets us measure how 'stable' a point is.
    """
    def __init__(self, max_iterations: int, escape_radius: float):
        self.max_iterations = max_iterations
        # Use squared radius so we avoid taking square roots in the loop
        self.escape_radius_squared = escape_radius * escape_radius

    def stability(self, c: complex, smooth: bool = True) -> float:
        """
        Return a stability value between 0 and 1.
        1.0 means the point never escaped (likely inside the set).
        Values closer to 0 mean it escaped quickly.
        """
        z = 0 + 0j

        for n in range(self.max_iterations):
            z = z * z + c
            # Check |z|^2 > escape_radius^2 (faster than using abs(z))
            if (z.real * z.real + z.imag * z.imag) > self.escape_radius_squared:
                # Simple normalized escape value
                return n / self.max_iterations

        # If we never escaped, treat it as fully stable (inside the set)
        return 1.0


def shading(hue_degrees: int, saturation: float, brightness: float):
    """
    Turn hue, saturation, and brightness values into an RGB color.
    Uses an HSV string like 'hsv(120,50%,80%)' and converts it to (R, G, B).
    """
    return getrgb(
        f"hsv({hue_degrees % 360},{saturation * 100}%,{brightness * 100}%)"
    )


if __name__ == "__main__":
    print("This might take a while...")

    # Create a MandelbrotSet object with tuning parameters
    mandelbrot_set = MandelbrotSet(max_iterations=25, escape_radius=1200)

    # Create a blank RGB image where we'll draw the fractal
    image = Image.new(mode="RGB", size=(1024, 1024))

    # Viewport maps each image pixel to a complex number (x + yi)
    # center and width control what part of the Mandelbrot set we see
    for pixel in Viewport(image, center=-0.75, width=3.5):
        # Convert pixel's position to a complex number and measure its stability
        stability = mandelbrot_set.stability(complex(pixel), smooth=True)

        # If stability == 1, the point is considered inside the set -> color it black
        # Otherwise, use the stability value to pick a color with the shading function
        pixel.color = (
            (0, 0, 0)
            if stability == 1
            else shading(
                hue_degrees=int(stability * 360),
                saturation=stability,
                brightness=1,
            )
        )

    # Display the generated Mandelbrot image
    image.show()

