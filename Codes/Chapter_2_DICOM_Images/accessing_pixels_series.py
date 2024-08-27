import itk

def read_series_of_images_tags(input_dir):
    # Setup the image readers with their type
    PixelType = itk.ctype("signed short")
    Dimension = 3

    ImageType = itk.Image[PixelType, Dimension]

    # Using GDCMSeriesFileNames to generate the names of
    # DICOM files.
    namesGenerator = itk.GDCMSeriesFileNames.New()
    namesGenerator.SetUseSeriesDetails(True)
    namesGenerator.SetDirectory(input_dir)

    # Get the names of files
    fileNames = namesGenerator.GetInputFileNames()

    # Setup the image series reader using GDCMImageIO
    reader = itk.ImageSeriesReader[ImageType].New()
    dicomIO = itk.GDCMImageIO.New()
    dicomIO.LoadPrivateTagsOn()
    reader.SetImageIO(dicomIO)
    reader.SetFileNames(fileNames)

    # Attempt to read the series, exit if unable to.
    try:
        reader.Update()
    except:
        print("Error occured while reading DICOMs in: " + input_dir)

    # ITK internally queries GDCM and obtains all the DICOM tags from the file
    # headers. The tag values are stored in the MetaDataDictionary
    # which is a general-purpose container for \{key,value\} pairs. The Metadata
    # dictionary can be recovered from any ImageIO class by invoking the
    # GetMetaDataDictionary() method.
    metadata = dicomIO.GetMetaDataDictionary()

    # Print the key value pairs from the metadadictionary
    tagkeys = metadata.GetKeys()

    for tagkey in tagkeys:
        # Note the [] operator for the key
        try:
            tagvalue = metadata[tagkey]
            print(tagkey + "=" + str(tagvalue))
        except RuntimeError:
            # Cannot pass specialized values into metadata dictionary.
            print("Cannot pass specialized value" + tagkey + "into metadadictionary")

    print("\n########################\n\n###########################\n")

    entryIDs = ["0010|0010","0010|0020","0008|1030","0008|103e","0008|0021","0020|000d","0020|000e","0020|0013","7fe0|0010"]

    for entryID in entryIDs:
        if not metadata.HasKey(entryID):
            print("tag: " + entryID + " not found in series")
        else:
            # The second parameter is mandatory in python to get the
            # string label value
            label = itk.GDCMImageIO.GetLabelFromTag(entryID, "")
            tagvalue = metadata[entryID]
            print(label[1] + " (" + entryID + ") is: " + str(tagvalue))

input_dir = "./images/DICOMSeries"
read_series_of_images_tags(input_dir=input_dir)        