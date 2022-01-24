import matplotlib.pyplot as plt
from Steganography import *

photo_path = input('image: ')
message_str = input('message: ')
pic = Image.open(photo_path, 'r')
shape = np.array(pic).shape


if len(shape) != 3:
    print(f'invalid shape size: {len(shape)}')
    exit()


num_bytes = 1
for n in np.array(pic).shape:
    num_bytes *= n
num_bytes /= 8

print(f'max bytes: {num_bytes}')
print(f'bytes needed: {len(message_str)}')


if len(message_str) < num_bytes:
    new_image = write_to_image(pic, message_str)

    # plt.imshow(pic)
    # plt.show()
    #
    # plt.imshow(new_image)
    # plt.show()

    decoded_message = decode_image(new_image)
    print(decoded_message)
    print(photo_path)

    new_image.save(photo_path)
