package main

import (
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/jpeg"
	"image/png"
	"io/ioutil"
	"log"
	"os"
	"reflect"
	"strconv"
	"strings"
)

// initialize by registering known image types
func init() {
	image.RegisterFormat("jpeg", "jpeg", jpeg.Decode, jpeg.DecodeConfig)
	image.RegisterFormat("png", "png", png.Decode, png.DecodeConfig)
}

// ChangeableImage interface needed to use Set method to change pixel values
type ChangeableImage interface {
	image.Image
	Set(x, y int, c color.Color)
}

type Img struct {
	cimg   ChangeableImage
	width  int
	height int
}

// can insert color.color and get pixel array
func rgbaToArray(r uint32, g uint32, b uint32, a uint32) [4]uint8 {
	return [4]uint8{uint8(r / 257), uint8(g / 257), uint8(b / 257), uint8(a / 257)}
}

// IsInstance returns boolean test if object is of certain type
func IsInstance(objectPtr, typePtr interface{}) bool {
	return reflect.TypeOf(objectPtr) == reflect.TypeOf(typePtr)
}

// get binary array of byte representing uint8 input x
func getBinArray(x uint8) [8]uint8 {
	a := int64(x)
	binStr := strconv.FormatInt(a, 2)
	binStr = fmt.Sprintf("%08s", binStr)
	var bitarray [8]uint8
	for i, s := range binStr {
		o, _ := strconv.Atoi(string(s))
		bitarray[i] = uint8(o)
	}
	return bitarray
}

// gets an image in the proper format given a string path
func getImg(path string) Img {
	imgFile, err := os.Open(path)
	if err != nil {
		fmt.Println("problem reading image")
		log.Fatal(err)
	}
	defer imgFile.Close()
	img, _, err := image.Decode(imgFile)
	if err != nil {
		fmt.Println("problem reading image but file exists")
		log.Fatal(err)
	}

	// if image is not in right formant, convert it
	if !IsInstance(img, (*image.RGBA)(nil)) {
		m := image.NewRGBA(image.Rect(0, 0, img.Bounds().Dx(), img.Bounds().Dy()))
		draw.Draw(m, m.Bounds(), img, img.Bounds().Min, draw.Src)
		img = m
	}

	cimg, ok := img.(ChangeableImage)
	if !ok {
		print("problem converting image to changeable image")
		panic(ok)
	}
	return Img{height: img.Bounds().Dy(), width: img.Bounds().Dx(), cimg: cimg}
}

// inserts a message into an image by altering the least significant bit of each
// pixel to represent a bit string of the bytes of each character in our message
func (img *Img) insertMessage(message string) {
	asciiValues := []byte(message)
	asciiValues = append(asciiValues, 0)

	var nBits int = 8 * len(asciiValues)
	leftover := nBits % 3
	if leftover != 0 {
		nBits += 3 - leftover
	}

	binArray := make([]uint8, nBits)

	if nBits > img.width*img.height*3 {
		fmt.Println("max bits: ", img.width*img.height*3, " - given: ", nBits)
		log.Fatal("message is too big")
	}

	for i, x := range asciiValues {
		ba := getBinArray(x)
		for j, bit := range ba {
			binArray[i*8+j] = bit
		}
		for j := 0; j < leftover; j++ {
			binArray[len(asciiValues)+j] = 0
		}
	}

	for i := 0; i < nBits/3; i++ {
		startBaSlice := i * 3
		endBaSlice := (i + 1) * 3

		pixX := i % img.width
		pixY := i / img.height

		//image values for this pixel
		iv := rgbaToArray(img.cimg.At(pixX, pixY).RGBA())

		// bit array slice, no need to worry about edge cases
		baValues := binArray[startBaSlice:endBaSlice]

		//change lest significant bit of pixel value to message bit value
		for ind, val := range baValues {
			iv[ind] -= iv[ind] % 2
			iv[ind] += val
		}
		img.cimg.Set(pixX, pixY, color.RGBA{uint8(iv[0]), iv[1], iv[2], iv[3]})
	}

}

func (img *Img) extractMessage() string {
	keepGoing := true
	message := ""
	bitStr := ""

	for i := 0; keepGoing; i++ {

		pixX := i % img.width
		pixY := i / img.height

		//if i%5 == 0 {
		//	fmt.Println("at: ", i, " pixel: ", pixX, " ", pixY)
		//}

		//image values for this pixel
		iv := rgbaToArray(img.cimg.At(pixX, pixY).RGBA())

		// iterate over the 3 color channels, add the LSB to the bitStr and check for termination every byte
		for k := 0; k < 3 && keepGoing; k++ {
			bitStr = bitStr + fmt.Sprintf("%d", iv[k]%2)
			if len(bitStr)%8 == 0 {
				last := bitStr[len(bitStr)-8 : len(bitStr)]
				keepGoing = last != "00000000"
				if !keepGoing {
					bitStr = bitStr[0 : len(bitStr)-8]
					for j := 0; j < (len(bitStr) / 8); j++ {
						seg := bitStr[j*8 : (j+1)*8]
						num, _ := strconv.ParseInt(seg, 2, 8)
						message = message + fmt.Sprintf("%c", num)
					}
				}
			}
		}
	}
	return message
}

func readTextFile(filePath string) string {
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		fmt.Println("message file error")
		log.Fatal(err)
	}
	return string(content)
}

func (img *Img) saveImg(fname string) {
	f, err := os.Create(fname)
	if err != nil {
		fmt.Println("cannot create new image")
		log.Fatal(err)
	}
	defer f.Close()
	err = png.Encode(f, img.cimg)
	if err != nil {
		fmt.Println("cannot create new image")
		log.Fatal(err)
	}
}

func main() {

	// create flags
	readPtr := flag.Bool("read", false, "read text instead of write")
	fromFilePtr := flag.String("text_file", "", "file to get message from")
	inputImagePathPtr := flag.String("image", "", "image to write to")
	outPutImagePathPtr := flag.String("output_image", "", "optional path to new image with message")
	messagePtr := flag.String("message", "", "input message if using write")
	flag.Parse()

	switch *readPtr {
	case false:
		img := getImg(*inputImagePathPtr)

		// determine the output file name
		var saveFile string
		if *outPutImagePathPtr != "" {
			if strings.ToLower(*outPutImagePathPtr)[len(*outPutImagePathPtr)-4:] != ".png" {
				log.Fatal("output image must be .png file")
			} else {
				saveFile = *outPutImagePathPtr
			}
		} else {
			point := strings.Index(*inputImagePathPtr, ".")
			if point > 0 {
				saveFile = string(*inputImagePathPtr)[0:point] + ".png"

			} else {
				saveFile = string(*inputImagePathPtr)[0:] + ".png"
			}
		}

		// insert the message
		if *fromFilePtr != "" {
			img.insertMessage(readTextFile(*fromFilePtr))
		} else {
			img.insertMessage(*messagePtr)
		}

		// save the image
		img.saveImg(saveFile)
		fmt.Println("Message written to file: ", saveFile)
		break

	case true:
		// read message from file
		img := getImg(*inputImagePathPtr)
		println(img.extractMessage())
		break
	}

}
