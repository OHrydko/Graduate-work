import numpy as np
from PIL import Image
from cv2 import cv2
from matplotlib import pyplot as plt
from pytesseract import pytesseract


# find normalized_histogram, and its cumulative distribution function
def otsu(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    hist_norm = hist.ravel() / hist.max()
    Q = hist_norm.cumsum()

    bins = np.arange(256)

    fn_min = np.inf
    thresh = -1

    for i in range(1, 256):
        p1, p2 = np.hsplit(hist_norm, [i])  # probabilities
        q1, q2 = Q[i], Q[255] - Q[i]  # cum sum of classes
        b1, b2 = np.hsplit(bins, [i])  # weights

        # finding means and variances
        m1, m2 = np.sum(p1 * b1) / q1, np.sum(p2 * b2) / q2
        v1, v2 = np.sum(((b1 - m1) ** 2) * p1) / q1, np.sum(((b2 - m2) ** 2) * p2) / q2

        # calculates the minimization function
        fn = v1 * q1 + v2 * q2
        if fn < fn_min:
            fn_min = fn
            thresh = i

    final_img = img.copy()
    print(thresh)
    final_img[img > thresh] = 255
    final_img[img < thresh] = 0
    return final_img


if __name__ == '__main__':
    img = cv2.imread('test photo/2020-04-16 16.00.47.jpg')
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image = otsu(image)
    plt.imshow(image, cmap='gray')
    plt.title("thresh Image")
    plt.show()
    text = pytesseract.image_to_string(Image.fromarray(img), lang='ukr')
    print(text)
