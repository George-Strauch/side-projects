from Steganography import *

photo_path = input('image: ')
pic = Image.open(photo_path, 'r')

print(decode_image(pic))
