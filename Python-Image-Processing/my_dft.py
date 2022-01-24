import numpy as np
from numba import njit


'''
https://www.youtube.com/watch?v=YYGltoYEmKo
F[u,v] = SUM[m]: SUM[n]: I[m,n] * e^(-ium) * e^(-ivn)
'''

# global variables
pi = np.pi
sample_size = 0
period = 0
print_samples = 20
frequencies = 0


@njit
def get_coefficients(img):
    hg, wd = img.shape
    coef_matrix = np.zeros(shape=(frequencies, frequencies), dtype=np.complex128)  # (u, v)
    w = np.e ** complex(0, -period)

    for u in range(frequencies):  # vert f
        if u % print_samples == 0: print("getting, freqs, col ", u)
        for v in range(frequencies):  # horz f

            for m in range(hg):
                cu = w ** (m * u)
                for n in range(wd):
                    coef_matrix[u, v] = coef_matrix[u, v] + (img[m, n] * (w ** (n * v)) * cu) / (sample_size)

    return coef_matrix


@njit
def inverse_transform(img_shape, cm):
    newimg = np.zeros(shape=img_shape, dtype=np.float64)
    cm_shape = cm.shape
    w = np.e ** complex(0, period)

    for row_ind in range(sample_size):
        if row_ind % print_samples == 0: print('row done', row_ind, " of ", sample_size)
        for col in range(sample_size):

            for u in range(cm_shape[0]):
                for v in range(cm_shape[1]):
                    newimg[row_ind, col] = newimg[row_ind, col] + (
                                cm[u, v] * ((w ** (u * row_ind)) * (w ** (v * col)))).real

    return newimg


# for square photo only for now
def define_globals(img_ary):
    global sample_size, period, frequencies
    sample_size = img_ary.shape[0]
    frequencies = sample_size
    period = 2 * pi / sample_size


