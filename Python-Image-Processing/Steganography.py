from PIL import Image
import numpy as np


def message_to_bit_str(message):
    # cvt message to byte list
    bit_str = ''  # bytes of message str
    for c in message:
        bit_str += str(bin(ord(c)))[2:].zfill(8)
    bit_str += str(bin(10))[2:].zfill(8)
    return bit_str


def to_range(iter):
    return range(len(iter))


def write_to_image(pil_image, message):
    img = np.array(pil_image)
    message = message_to_bit_str(message)
    bit_index = 0
    for row in to_range(img):
        for pix in to_range(img[row]):
            for chan in to_range(img[row, pix]):
                num = img[row, pix, chan]

                if num % 2 == 1:
                    num -= 1

                num = num + int(message[bit_index])
                img[row, pix, chan] = num
                bit_index += 1
                if bit_index == len(message):
                    return Image.fromarray(img)


def decode_image(pil_image):
    img = np.array(pil_image)
    current_byte = ''
    message = ''
    for row in to_range(img):
        for pix in to_range(img[row]):
            for chan in to_range(img[row, pix]):
                num = img[row, pix, chan]

                if num % 2 == 1:
                    current_byte += '1'
                else:
                    current_byte += '0'

                if len(current_byte) == 8:
                    char_int = int(current_byte, 2)
                    message += chr(char_int)
                    current_byte = ''

                    if char_int == 10:
                        return message

