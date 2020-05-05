import math

import matplotlib.pyplot as plt
import numpy as np
from cv2 import cv2


def func(x, mu, sd):
    return 1 / (np.sqrt(2 * np.pi) * sd) * np.e ** (-np.power((x - mu) / sd, 2) / 2)


def gaussian_kernel(size, sigma=1, verbose=False):
    kernel_1 = np.linspace(-(size // 2), size // 2, size)
    for i in range(size):
        kernel_1[i] = func(kernel_1[i], 0, sigma)
    kernel_2 = np.outer(kernel_1.T, kernel_1.T)

    kernel_2 *= 1.0 / kernel_2.max()

    if verbose:
        plt.imshow(kernel_2, interpolation='none', cmap='gray')
        plt.title("Kernel ( {}X{} )".format(size, size))
        plt.show()

    return kernel_2


def gaussian_blur(image, kernel_size, verbose=False):
    kernel = gaussian_kernel(kernel_size, sigma=math.sqrt(kernel_size), verbose=verbose)
    return convolution(image, kernel, average=True, verbose=verbose)


def convolution(image, kernel, average=False, verbose=False):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if verbose:
        plt.imshow(image, cmap='gray')
        plt.title("Image")
        plt.show()

    image_row, image_col = image.shape
    kernel_row, kernel_col = kernel.shape

    output_img = np.zeros(image.shape)

    pad_height = int((kernel_row - 1) / 2)
    pad_width = int((kernel_col - 1) / 2)

    padded = np.zeros((image_row + (2 * pad_height), image_col + (2 * pad_width)))

    padded[pad_height:padded.shape[0] - pad_height, pad_width:padded.shape[1] - pad_width] = image

    if verbose:
        plt.imshow(padded, cmap='gray')
        plt.title("Padded Image")
        plt.show()

    for row in range(image_row):
        for col in range(image_col):
            output_img[row, col] = np.sum(kernel * padded[row:row + kernel_row, col:col + kernel_col])
            if average:
                output_img[row, col] /= kernel.shape[0] * kernel.shape[1]

    print("output_img Image size : {}".format(output_img.shape))

    if verbose:
        plt.imshow(output_img, cmap='gray')
        plt.title("output_img Image using {}X{} Kernel".format(kernel_row, kernel_col))
        plt.show()
    output_img = np.array(output_img, dtype=np.uint8)
    return output_img


if __name__ == '__main__':
    img = cv2.imread('test photo/2020-04-16 16.58.59.jpg')
    gaussian_blur(img, 9, True)
