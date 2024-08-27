# ITK internally queries GDCM and obtains all the DICOM tags from the file
# headers. The tag values are stored in the MetaDataDictionary
# which is a general-purpose container for \{key,value\} pairs. The Metadata
# dictionary can be recovered from any ImageIO class by invoking the
# GetMetaDataDictionary() method.


import itk
import matplotlib.pyplot as plt

def read_tags(input_file,plot=True):
    #define pixel type and dimensiom
    input_pixel_type = itk.SS
    input_dim = 2
    input_img_type = itk.Image[input_pixel_type,input_dim]

    #create reader and set filename
    reader = itk.ImageFileReader[input_img_type].New()
    reader.SetFileName(input_file)

    gdcmImageIO = itk.GDCMImageIO.New()
    gdcmImageIO.LoadPrivateTagsOn()
    reader.SetImageIO(gdcmImageIO)  


    # Read the image
    try:
        reader.Update()
    except Exception as e:
        print("Exception in file reader:", e)
        
    metadata = gdcmImageIO.GetMetaDataDictionary()

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

    #printing important dicom tags
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

    if plot:       
        # Convert the read image to a NumPy array and plot it
        input_image_array = itk.array_from_image(reader.GetOutput())
        plt.figure(figsize=(15, 10))
        plt.subplot(1, 3, 1)
        plt.title("Original Image")
        plt.imshow(input_image_array, cmap='gray')
        plt.axis('off')

input_file = "./images/DICOMSeries/Image0077/Image0077.dcm"

read_tags(input_file=input_file,plot=True)