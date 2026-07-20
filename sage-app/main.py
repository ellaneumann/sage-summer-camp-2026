from waggle.plugin import Plugin
from waggle.data.vision import Camera
import numpy as np


def compute_mean_color(image):
    return np.mean(image, (0, 1)).astype(float)


def main():
    input = "example.jpg"

    with Plugin() as plugin, Camera(input) as camera:
        snapshot = camera.snapshot()

        # compute mean color
        mean_color = compute_mean_color(snapshot.data)

        # print mean color
        print(mean_color)

        # publish color
        plugin.publish("color.mean.r", mean_color[0], timestamp=snapshot.timestamp)
        plugin.publish("color.mean.g", mean_color[1], timestamp=snapshot.timestamp)
        plugin.publish("color.mean.b", mean_color[2], timestamp=snapshot.timestamp)




if __name__ == "__main__":
    main()
