import numpy as np
from PIL import Image
import timeit
import filter, view, my_dft


def just_get_array(file):
    img = Image.open(file)
    im_array = np.array(img, dtype=np.uint8)

    if len(im_array.shape) == 3:
        print("here")
        im_array = filter.make_2d(im_array)

    # if im_array.size > 500*500:
    #     im_array = filter.scale_down(im_array, 4)
    #     pass

    return filter.make_square(im_array)

# ------------------------------------------------------------------
fl = '../imgs/nums/1764.png'


im = just_get_array(fl)
view.show_image(im)



def my_implementation():
    my_dft.define_globals(im)   # todo, make this done automatically

    c = my_dft.get_coefficients(im)
    view.display_c(c)
    img = my_dft.inverse_transform(im.shape, c)
    view.show_image(img)



def np_implementation():
    c = np.fft.fft2(im)
    view.display_c(c)
    img = np.fft.ifft2(c)
    view.show_image(img.real.astype(np.float32))


print(timeit.timeit("my_implementation()", setup="from __main__ import my_implementation", number=1), " seconds for my code")
print(timeit.timeit("np_implementation()", setup="from __main__ import np_implementation", number=1), " seconds for np code")
