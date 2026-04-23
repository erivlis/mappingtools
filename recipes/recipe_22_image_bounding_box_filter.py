"""
Recipe 22: Image Bounding Box Filter (reshape + Lenses)

In image processing, an image might be represented as a flat stream of pixels
(e.g., from a sensor or linear array) with x, y coordinates and RGB values.

This recipe uses `reshape` to convert a flat array of pixels into a 2D spatial
tensor (Y -> X -> RGB). Then, it uses a `Lens` to target a specific "bounding box"
or pixel and immutably apply a color filter (like Grayscale),
leaving the rest of the image pristine.
"""

from mappingtools.operators import reshape
from mappingtools.optics import Lens


def main():
    # 1. A 3x3 Image represented as a flat stream of pixel data
    # (x, y, r, g, b)
    pixel_stream = [
        {"x": 0, "y": 0, "r": 255, "g": 0, "b": 0},   # Red
        {"x": 1, "y": 0, "r": 0, "g": 255, "b": 0},   # Green
        {"x": 2, "y": 0, "r": 0, "g": 0, "b": 255},   # Blue

        {"x": 0, "y": 1, "r": 255, "g": 255, "b": 0}, # Yellow
        {"x": 1, "y": 1, "r": 0, "g": 255, "b": 255}, # Cyan
        {"x": 2, "y": 1, "r": 255, "g": 0, "b": 255}, # Magenta

        {"x": 0, "y": 2, "r": 255, "g": 255, "b": 255}, # White
        {"x": 1, "y": 2, "r": 128, "g": 128, "b": 128}, # Gray
        {"x": 2, "y": 2, "r": 0, "g": 0, "b": 0},       # Black
    ]

    # 2. Reshape into a 2D Spatial Tensor (Row Y -> Col X -> RGB Dict)
    image_tensor = reshape(
        pixel_stream,
        keys=["y", "x"],
        value=lambda p: {"r": p["r"], "g": p["g"], "b": p["b"]}
    )

    print("--- Original 2D Image Tensor (Row Y=1) ---")
    import json
    print(json.dumps(image_tensor[1], indent=2))

    # 3. Define an Image Filter (e.g., Grayscale)
    def to_grayscale(pixel):
        # Luma coding (perceived brightness)
        gray = int(0.299 * pixel["r"] + 0.587 * pixel["g"] + 0.114 * pixel["b"])
        return {"r": gray, "g": gray, "b": gray}

    # 4. Create an Optic to focus on a specific bounding region
    # We want to apply the filter ONLY to the center pixel (y=1, x=1) which is Cyan (0, 255, 255)
    center_pixel_lens = Lens.path(1, 1)

    # 5. Immutably apply the filter
    filtered_image = center_pixel_lens.modify(image_tensor, to_grayscale)

    print("\n--- Filtered Image Tensor (Center Pixel Grayscaled) ---")
    print(json.dumps(filtered_image[1], indent=2))

    print("\n--- Verification: Original Image is Untouched ---")
    print(json.dumps(image_tensor[1][1]))


def test_main():
    main()


if __name__ == "__main__":
    main()
