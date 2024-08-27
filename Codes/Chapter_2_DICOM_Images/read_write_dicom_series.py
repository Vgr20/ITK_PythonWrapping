import itk
import os
import matplotlib.pyplot as plt

def convert_3d_to_2d_dicom(input_dir, output_dir):
    # Define types
    PixelType = itk.F
    Dimension = 3
    ImageType = itk.Image[PixelType, Dimension]
    
    # Create an ImageSeriesReader
    reader = itk.ImageSeriesReader[ImageType].New()
    
    # Setup GDCMImageIO and NamesGenerator
    gdcm_io = itk.GDCMImageIO.New()
    names_generator = itk.GDCMSeriesFileNames.New()
    names_generator.SetInputDirectory(input_dir)
    
    filenames = names_generator.GetInputFileNames()
    reader.SetImageIO(gdcm_io)
    reader.SetFileNames(filenames)
    
    # Read the 3D volume
    reader.Update()
    image_3d = reader.GetOutput()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define types for writing 2D slices
    OutputPixelType = itk.F
    OutputDimension = 2
    Image2DType = itk.Image[OutputPixelType, OutputDimension]
    series_writer = itk.ImageSeriesWriter[ImageType, Image2DType].New()
    
    # Configure the ImageSeriesWriter
    series_writer.SetInput(image_3d)
    series_writer.SetImageIO(gdcm_io)
    names_generator.SetOutputDirectory(output_dir)
    output_filenames = names_generator.GetOutputFileNames()
    series_writer.SetFileNames(output_filenames)
    
    # Copy metadata
    series_writer.SetMetaDataDictionaryArray(reader.GetMetaDataDictionaryArray())
    
    try:
        series_writer.Update()
        print("Conversion Successful")
    except itk.ExceptionObject as excp:
        print("Exception thrown while writing the series:")
        print(excp)
        

input_dir = "./images/OneDrive_2024-08-17/DICOM images"
output_dir = "./images/OneDrive_2024-08-17/DICOM images/DICOM"
convert_3d_to_2d_dicom(input_dir,output_dir)