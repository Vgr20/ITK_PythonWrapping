import os
import itk
import matplotlib.pyplot as plt

input_file = "./images/Vida_Head.MR.Comp_DR-Gain_DR.1005.1.2021.04.27.14.20.13.818.14380335.dcm"

image = itk.imread(input_file)

# Convert the read image to a NumPy array and plot it
input_image_array = itk.array_from_image(image)[0]
plt.figure(figsize=(15, 10))
plt.subplot(1, 3, 1)
plt.title("Original Image")
plt.imshow(input_image_array, cmap='gray')
plt.axis('off')