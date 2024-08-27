import itk
import os
import matplotlib.pyplot as plt

def convert_2d_3d(input_dir,series=0,dim=3):
    # Define the pixel type and dimension
    pixel_type = itk.ctype("signed short")

    # Create the image type
    img_type = itk.Image[pixel_type, dim]

    # Create a GDCM series file names generator
    name_generator = itk.GDCMSeriesFileNames.New()
    name_generator.SetUseSeriesDetails(True)
    name_generator.AddSeriesRestriction("0008|0021")
    name_generator.SetGlobalWarningDisplay(False)
    name_generator.SetDirectory(input_dir)

    # Get the series UIDs
    series_UID = name_generator.GetSeriesUIDs()
 

    if len(series_UID) < 1:
        print("No DICOMs in: " + input_dir)
    else:
        print("Found series UID(s):", series_UID)

        # Select the first series UID
        series_identifier = series_UID[series]

        # Get the file names for the series
        file_names = name_generator.GetFileNames(series_identifier)
        print(file_names)

        # Create the series reader
        series_reader = itk.ImageSeriesReader[img_type].New()
        series_reader.SetFileNames(file_names)


        dicomIO = itk.GDCMImageIO.New()
        series_reader.SetImageIO(dicomIO)
        series_reader.ForceOrthogonalDirectionOff()

        try:
            # Update the reader to load the image
            series_reader.Update()
            image = series_reader.GetOutput()
            print(f"Successfully read DICOM series into 3D image with size: {image.GetLargestPossibleRegion().GetSize()}")
        except Exception as e:
            print("Error reading DICOM series:", e)


        writer = itk.ImageFileWriter[img_type].New()
        outFileName = os.path.join(input_dir, series_identifier + ".nrrd")
        writer.SetFileName(outFileName)
        writer.UseCompressionOn()
        writer.SetInput(series_reader.GetOutput())
        print("Writing: " + outFileName)
        writer.Update()

input_dir= "./images/DICOMSeries"
series = 0
dim = 3
convert_2d_3d(input_dir=input_dir,series=series,dim=dim)