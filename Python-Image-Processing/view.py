import numpy as np
import matplotlib.pyplot as plt



def display_c(c):
    j = np.zeros(c.shape)

    for row in range(c.shape[0]):
        for col in range(c.shape[1]):
            j[row, col] = np.log(1+abs(c[row,col]))

    plt.imshow(j)
    plt.show()


def show_pix_mags(aray):
    na = aray.reshape(1, aray.size)[0]
    plt.hist(na, bins=10)
    plt.show()

def show_image(image):
    plt.imshow(image)
    plt.show()
