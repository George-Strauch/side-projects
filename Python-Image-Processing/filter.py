import numpy as np
from numba import njit
import view
import math

# global variables
pi = np.pi


def scale_down(img, sq_factor):
    print(img.shape)
    height, width = img.shape
    new_h = height//sq_factor
    new_w = width//sq_factor
    new_img = []

    for i in range(new_h):
        row = []
        for j in range(new_w):
            sum_var = 0
            for a in range(sq_factor):
                for b in range(sq_factor):
                    sum_var += img[i * sq_factor + a, j * sq_factor + b]
            row.append(sum_var / sq_factor ** 2)

        new_img.append(row)
    return np.array(new_img)



# handles the njit functions
def edge_detect(image, thresh):

    view.show_image(image)
    # view.show_pix_mags(image)
    # image = inverse_img(image)
    # view.show_pix_mags(image)
    # view.show_image(image)

    coefs = np.fft.fft2(image)
    coefs = freq_filter(np.fft.fftshift(coefs), thresh, 'high')
    image = np.fft.ifft2(np.fft.fftshift(coefs)).real.astype(np.float64)
    image = increase_pix_vals(image)

    view.display_c(coefs)

    view.show_pix_mags(image)
    view.show_image(image)
    return edge_filter_no_python(image)


@njit
def inverse_img(img):
    m = img.max()
    return m-img.astype(np.float64)


@njit
def increase_pix_vals(img):
    mn = img.min()
    return img-mn

@njit
def freq_filter(cc_shifted, thresh, pass_type):
    # cc: shifted complex coefficients
    # pass_type: string that is either 'low' or 'high'
    # returns new cc array still shifted
    thresh /= 100
    min_val = min(cc_shifted.shape) / 2
    xor = False
    if pass_type == 'low':
        xor = True

    # default as high pass, meaning only lower frequencies will remain.
    # if pt == high, then xor with True (var xor) to not the output
    for i in range(cc_shifted.shape[0]):
        for k in range(cc_shifted.shape[1]):
            if xor ^ (((cc_shifted.shape[0]//2 - i)**2 + (cc_shifted.shape[1]//2 - k)**2) < (thresh*(min_val**2))):
                cc_shifted[i, k] = 0

    return cc_shifted


@njit
def edge_filter_no_python(image):
    # expects image to be type uint8
    # returns new uint8 image array with 1 for edge and o else

    half = np.mean(image)*1.15  # todo alter this based on variance
    print("half: ", half)
    for i in range(image.shape[0]):
        for k in range(image.shape[1]):
            if image[i, k] >= half:
                image[i, k] = 1
            else:
                image[i, k] = 0
    return image.astype(np.uint8)


@njit
def gen_circle(diameter):
    grid = np.zeros((diameter, diameter), dtype=np.uint8)
    radius = diameter/2   # also the center of the circle from pix grid
    for x in range(diameter):
        for y in range(diameter):
            if ((y-radius)**2 + (x - radius)**2) <= radius**2:
                grid[x, y] = 1
    return grid



@njit
def make_2d(img_array):
    a, b, c = img_array.shape
    new_array = np.zeros((a, b), dtype=img_array.dtype)
    for i in range(a):
        for j in range(b):
            sm = 0
            for k in range(c):
                sm += img_array[i, j, k]
            new_array[i, j] = sm//c
    return new_array



# applies kernel both horizontally and vertically
@njit
def apply_1d_kernel(img, kernel):
    mid = len(kernel) // 2
    height, width, _ = img.shape
    ker_len = len(kernel)
    tmp_ker = kernel

    new_image = np.empty(shape=(height, width, 3), dtype=np.uint8)

    # first go horizontally
    for row in range(height):
        for pixel in range(width):
            if mid > pixel:
                start = mid-pixel
                finish_p1 = ker_len

            elif ker_len-mid > width-pixel:
                start = 0
                finish_p1 = mid+(width-pixel)

            else:
                start = 0
                finish_p1 = ker_len
            # print("row, pix: ", row, pixel, " --- start, finish(+1): ", start, finish_p1)
            for color in range(3):
                sum_var = 0
                for i in range(start, finish_p1):
                    sum_var += tmp_ker[i] * img[row, pixel+i-mid, color]
                new_image[row, pixel, color] = sum_var

    # then go vertically
    for row in range(height):
        if mid > row:
            start = mid - row
            finish_p1 = ker_len

        elif ker_len - mid > height - row:
            start = 0
            finish_p1 = mid + (height - row)

        else:
            start = 0
            finish_p1 = ker_len

        for pixel in range(width):
            for color in range(3):
                sum_var = 0
                for i in range(start, finish_p1):
                    sum_var += kernel[i] * new_image[row+i-mid, pixel, color]
                new_image[row, pixel, color] = sum_var

    return new_image



# # applies kernel with loss of pixels on borders
@njit
def apply_kernel(img, kernel):
    height, width, _ = img.shape
    ker_len = kernel.shape[0]
    new_image = np.empty(shape=(height-ker_len, width-ker_len, 3), dtype=np.uint8)

    for row_ind in range(height-ker_len):
        for pix_ind in range(width-ker_len):
            for color in range(3):
                sm = 0
                for i in range(ker_len):
                    for v in range(ker_len):
                        sm = sm + kernel[i, v] * img[row_ind+i, pix_ind+v, color]
                new_image[row_ind, pix_ind, color] = sm

    return new_image




# std = standard deviation
@njit
def make_gauss_blur_kernel(std, sq_size=3):
    kernel = np.empty(shape=(sq_size, sq_size))
    mid = sq_size//2
    for i in range(sq_size):
        for j in range(sq_size):
            # dist = ((mid-i)**2 + (mid-j)**2)**.5
            # kernel[i, j] = round(norm_dist(std, dist), 5)
            kernel[i, j] = norm_dist_2d(std, (mid-i), (mid-j))

    return normalize_kernel(kernel)




@njit
def make_1d_gaussian_kernel(std, l=3):
    kernel = np.empty(shape=(l,))
    mid = l//2
    for i in range(l):
        kernel[i] = norm_dist(std, (i-mid))
    return normalize_1d_kernel(kernel)


@njit
def norm_dist(std, dist):
    return (1 / (std*(2*math.pi)**.5)) * (math.e**(-1*(dist**2) / (2*(std**2))))


@njit
def norm_dist_2d(std, x, y):
    return (1 / (std*(2*math.pi)**.5)) * (math.e**(-1*(x**2 + y**2) / (2*(std**2))))


@njit
def normalize_1d_kernel(kernel):
    weight_sum = 0
    l = len(kernel)
    # get sum of weights
    for i in range(l):
            weight_sum += kernel[i]

    if 1-weight_sum < 0.03:
        return kernel

    for i in range(l):
        kernel[i] = kernel[i] / weight_sum

    return kernel


@njit
def normalize_kernel(kernel):
    weight_sum = 0
    h, w = kernel.shape
    # get sum of weights
    for i in range(h):
        for k in range(w):
            weight_sum += kernel[i, k]

    print('weight is: ', weight_sum)

    for i in range(h):
        for k in range(w):
            kernel[i, k] = kernel[i, k] / weight_sum

    return kernel


@njit
def make_square(img):
    height, width = img.shape
    mn = min(height, width)
    return img[0:mn, 0:mn]




