# GenerateUltronCore.py
from PIL import Image, ImageDraw
import numpy as np
import imageio.v2 as imageio

def create_ultron_core_gif(path="UltronCore.gif", size=512, frames_count=40):
    frames = []
    max_radius = size // 2 - 20
    for i in range(frames_count):
        img = Image.new("RGB", (size, size), "black")
        draw = ImageDraw.Draw(img)
        t = i / frames_count
        intensity = int(180 + 75 * np.sin(t * 2 * np.pi))
        color = (intensity, 0, 0)
        radius = int(max_radius * (0.7 + 0.3 * np.sin(t * 2 * np.pi)))
        for r in range(0, radius, 8):
            draw.ellipse(
                (size/2 - r, size/2 - r, size/2 + r, size/2 + r),
                outline=color,
                width=2
            )
        draw.ellipse(
            (size/2 - 20, size/2 - 20, size/2 + 20, size/2 + 20),
            fill=(255, 30, 30)
        )
        frames.append(img)
    frames[0].save(
        path, save_all=True, append_images=frames[1:], duration=80, loop=0
    )
    print(f"✅ {path} created")

if __name__ == "__main__":
    create_ultron_core_gif()
