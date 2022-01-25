# Steganography using lest significant bit in GOLANG
Steganography is used to hide messages in objects. In this implementation,
we are storing text in images by altering the least significant bit of each color
channel of pixels to store a binary string representing a message. Changing the 
least significant bit only changes the value by at most one which is unnoticeable to 
the human eye when observing the image. A character in a string can be represented by its
ASCII value which is an 8-bit number. Therefore, a character can be stored in less than
3 Pixels since each pixel has 3 channels.

# Instructions
```bash
> go build steganography.go 
> ./steganography -image <image> -text_file <*.txt>
> ./steganography -image <image> -message "message"
> ./steganography -read -image <image>
```

