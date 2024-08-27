import itk
import os
import matplotlib.pyplot as plt

input_file = "./images/Vida_Head.MR.Comp_DR-Gain_DR.1005.1.2021.04.27.14.20.13.818.14380335.dcm"

#define pixel type and dimensiom
input_pixel_type = itk.SS
input_dim = 2
input_img_type = itk.Image[input_pixel_type,input_dim]

#create reader and set filename
reader = itk.ImageFileReader[input_img_type].New()
reader.SetFileName(input_file)

# Read the image
try:
    reader.Update()
except Exception as e:
    print("Exception in file reader:", e)
    
# Convert the read image to a NumPy array and plot it
input_image_array = itk.array_from_image(reader.GetOutput())
plt.figure(figsize=(15, 10))
plt.subplot(1, 3, 1)
plt.title("Original Image")
plt.imshow(input_image_array, cmap='gray')
plt.axis('off')