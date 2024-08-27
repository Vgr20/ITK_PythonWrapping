import itk
import os
import matplotlib.pyplot as plt


def update_header(input_file,output_file,entry_id,value):
    InputPixelType = itk.SS  # short
    Dimension = 2
    InputImageType = itk.Image[InputPixelType, Dimension]

    # Reader
    reader = itk.ImageFileReader[InputImageType].New()
    reader.SetFileName(input_file)

    # GDCM Image IO
    gdcmImageIO = itk.GDCMImageIO.New()
    reader.SetImageIO(gdcmImageIO)
    reader.Update()

    input_image = reader.GetOutput()

    # Metadata dictionary
    dictionary = input_image.GetMetaDataDictionary()

    label = itk.GDCMImageIO.GetLabelFromTag(entry_id, "")
    tagvalue = dictionary[entry_id]
    print("Current" + label[1] + " (" + entry_id + ") is: " + str(tagvalue))
        
    if dictionary.HasKey(entry_id):
        dictionary[entry_id] = value
    else:
        itk.MetaDataObject[str].SetMetaData(dictionary, entry_id, value)

    # Writer
    writer = itk.ImageFileWriter[InputImageType].New()
    writer.SetInput(reader.GetOutput())
    writer.SetFileName(output_file)
    writer.SetImageIO(gdcmImageIO)
    writer.Update()


input_file = "./images/OneDrive_2024-08-17/IM-0001-0031.dcm"
output_file = "./images/OneDrive_2024-08-17/metadata_changed/Metadata_changed_IM-0001-0031.dcm"
entry_id = "0010|0010"
value = "Asini Jayakody"

update_header(input_file,output_file,entry_id,value)