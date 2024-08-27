#Note that these two methods are
#relatively slow and should not be used in situations where high-performance access is required.
#Image iterators are the appropriate mechanism to efficiently access image pixel data. 

import itk

# reading the input image
input_file = './images/DICOM'

input_pixel_type = itk.SS
input_dim = 2
input_img_type = itk.Image[input_pixel_type,input_dim]

reader = itk.ImageFileReader[input_img_type].New()
reader.SetFileName(input_file)

# Read the image
try:
    reader.Update()
except Exception as e:
    print("Exception in file reader:", e)

pixel_index = itk.Index[2]()  # Create a 2D index (change to itk.Index[2] for 2D images)
pixel_index[0] = 0  # X coordinate
pixel_index[1] = 0  # Y coordinate

image = reader.GetOutput()
# Get the pixel value at the specified index
pixel_value = image.GetPixel(pixel_index)
print(f"Original pixel value at {pixel_index}: {pixel_value}")

new_pixel_value = 255

# Set the new pixel value at the specified index
image.SetPixel(pixel_index, new_pixel_value)

# Verify the change
print(f"New pixel value at {pixel_index}: {image.GetPixel(pixel_index)}")