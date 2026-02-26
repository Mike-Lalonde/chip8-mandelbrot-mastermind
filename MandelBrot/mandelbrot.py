from dataclasses import dataclass
from typing import Tuple, List
import math

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


# ==========================
#  Mandelbrot core
# ==========================

@dataclass
class MandelbrotSet:
    max_iterations: int = 200
    escape_radius: float = 2.0

    def escape_count(self, c: complex) -> int:
        """
        Return the integer iteration count at which the orbit of c
        escapes beyond the escape radius. If it never escapes within
        max_iterations, return max_iterations.
        """
        z = 0 + 0j
        r2 = self.escape_radius * self.escape_radius

        for n in range(self.max_iterations):
            # Check magnitude squared to avoid a sqrt
            if (z.real * z.real + z.imag * z.imag) > r2:
                return n
            z = z * z + c

        return self.max_iterations

    def stability(self, c: complex, smooth: bool = True) -> float:
        """
        Return a floating-point "stability" value in [0, 1], where values
        closer to 1 are more stable (either inside or near the set) and
        values near 0 are fast-escaping points.

        If smooth=True, use a continuous coloring formula instead of
        coarse integer iteration counts.
        """
        z = 0 + 0j
        r2 = self.escape_radius * self.escape_radius

        for n in range(self.max_iterations):
            z = z * z + c
            mag2 = z.real * z.real + z.imag * z.imag

            if mag2 > r2:
                # The point escaped at iteration n.
                if smooth:
                    # Smooth coloring (continuous escape time)
                    # t = n + 1 - log(log|z|) / log 2
                    mag = math.sqrt(mag2)
                    smooth_iter = n + 1 - math.log(math.log(mag, 2), 2)
                    # Normalize to [0, 1]
                    v = smooth_iter / self.max_iterations
                else:
                    v = n / self.max_iterations

                # Convert to "stability": inside ≈ 1, outside ≈ 0
                return max(0.0, min(1.0, 1.0 - v))

        # Did not escape: treat as fully stable
        return 1.0


# ==========================
#  Viewport / Pixel helpers
# ==========================

@dataclass
class Viewport:
    image: Image.Image          # Pillow image
    center: complex             # Center point in complex plane
    width: float                # Width of view in complex plane

    @property
    def height(self) -> float:
        """Height in complex plane, adjusted for image aspect ratio."""
        w, h = self.image.size
        aspect = h / w
        return self.width * aspect

    @property
    def scale(self) -> float:
        """
        Complex units per pixel horizontally.
        (Same scale vertically because we keep aspect ratio.)
        """
        w, _ = self.image.size
        return self.width / w

    @property
    def offset(self) -> complex:
        """
        Complex coordinate of the top-left pixel.
        """
        return complex(
            self.center.real - self.width / 2,
            self.center.imag + self.height / 2
        )

    def __iter__(self):
        """Iterate over all pixels in the viewport as Pixel objects."""
        w, h = self.image.size
        for y in range(h):
            for x in range(w):
                yield Pixel(self, x, y)


@dataclass
class Pixel:
    viewport: Viewport
    x: int
    y: int

    @property
    def color(self) -> Tuple[int, int, int]:
        return self.viewport.image.getpixel((self.x, self.y))

    @color.setter
    def color(self, rgb: Tuple[int, int, int]):
        self.viewport.image.putpixel((self.x, self.y), rgb)

    def to_complex(self) -> complex:
        """
        Map pixel (x, y) to a complex coordinate based on the viewport.
        """
        offset = self.viewport.offset
        scale = self.viewport.scale
        # Note: y increases downward in image space, but imaginary axis
        # increases upward, so we subtract.
        return complex(
            offset.real + self.x * scale,
            offset.imag - self.y * scale
        )

    def __complex__(self) -> complex:
        return self.to_complex()


# ==========================
#  Color utilities
# ==========================

def make_palette(colormap_name: str, size: int = 256) -> List[Tuple[int, int, int]]:
    """
    Build an RGB palette (list of (r, g, b)) using a Matplotlib colormap.
    """
    cmap = plt.get_cmap(colormap_name)
    palette: List[Tuple[int, int, int]] = []

    for i in range(size):
        # value between 0 and 1
        t = i / (size - 1)
        r, g, b, _ = cmap(t)
        palette.append((
            int(r * 255),
            int(g * 255),
            int(b * 255),
        ))

    return palette


def paint(viewport: Viewport, mset: MandelbrotSet, palette: List[Tuple[int, int, int]]):
    """
    Render the Mandelbrot set into the given viewport using the supplied palette.
    The palette is indexed by stability value.
    """
    n_colors = len(palette)

    for pixel in viewport:
        c = complex(pixel)
        s = mset.stability(c, smooth=True)   # 0..1
        # Map stability to palette index
        idx = int(s * (n_colors - 1))
        pixel.color = palette[idx]


# ==========================
#  Main script
# ==========================

def main():
    # Image parameters
    width_px = 800
    height_px = 600

    # Create a blank RGB image (black)
    image = Image.new("RGB", (width_px, height_px), (0, 0, 0))

    # Define which part of the complex plane to view
    # (this is a classic initial view)
    center = complex(-0.75, 0.0)
    view_width = 3.5

    viewport = Viewport(image=image, center=center, width=view_width)

    # Create Mandelbrot set object
    mset = MandelbrotSet(max_iterations=300, escape_radius=2.0)

    # Build a nice color palette (try "turbo", "plasma", "twilight", etc.)
    palette = make_palette("turbo", size=512)

    # Render
    print("Rendering Mandelbrot set, please wait...")
    paint(viewport, mset, palette)
    print("Done!")

    # Save to file
    output_file = "mandelbrot_color.png"
    image.save(output_file, format="PNG")
    print(f"Saved image to {output_file}")

    # Optionally display using matplotlib
    plt.figure(figsize=(8, 6))
    plt.imshow(np.array(image))
    plt.axis("off")
    plt.title("Mandelbrot Set (colored)")
    plt.show()


if __name__ == "__main__":
    main()
