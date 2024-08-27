import itk
import os
import matplotlib.pyplot as plt

input_file = './images/DICOM'

input_pixel_type = itk.SS
input_dim = 2
input_img_type = itk.Image[input_pixel_type,input_dim]

reader = itk.ImageFileReader[input_img_type].New()
reader.SetFileName(input_file)

output_dcm_file_original = "./images/output_dcm_file_original.dcm"
output_rescaled_dcm_file = "./images/output_rescaled_dcm_file.dcm"
output_jpeg_file = "./images/output_jpeg_file.jpg"

gdcmImageIO = itk.GDCMImageIO.New()

# create a writer to save image back to DICOM file
writer1Type = itk.ImageFileWriter[input_img_type]
writer1 = writer1Type.New()
writer1.SetFileName(output_dcm_file_original)
writer1.SetInput(reader.GetOutput())
writer1.SetImageIO(gdcmImageIO)

try:
    writer1.Update()
except Exception as e:
    print("Exception in file writer:", e)

# Rescale the image intensity
write_pixel_type = itk.UC
write_img_type = itk.Image[write_pixel_type,input_dim]
rescale_filter_type = itk.RescaleIntensityImageFilter[input_img_type,write_img_type]

rescaler = rescale_filter_type.New()
rescaler.SetOutputMinimum(0)
rescaler.SetOutputMaximum(255)
rescaler.SetInput(reader.GetOutput())

writer2Type = itk.ImageFileWriter[write_img_type]
writer2 = writer2Type.New()
writer2.SetFileName(output_jpeg_file)
writer2.SetInput(rescaler.GetOutput())



try:
    writer2.Update()
except Exception as e:
    print("Exception in file writer:", e)

# writing rescaled image to dicom
writer3Type = itk.ImageFileWriter[write_img_type]
writer3 = writer3Type.New()
writer3.SetFileName(output_rescaled_dcm_file)
writer3.SetInput(rescaler.GetOutput())
writer3.UseInputMetaDataDictionaryOff()
writer3.SetImageIO(gdcmImageIO)

try:
    writer3.Update()
except Exception as e:
    print("Exception in file writer:", e)