import itk
import argparse

# Argument parser setup with flags
def main():
    parser = argparse.ArgumentParser(description="ITK Geodesic active contour Segmentation with Smoothing, Gradient, and Sigmoid Filters.")
    parser.add_argument("-x", "--seedX", type=int, required=True, help="X coordinate of the seed point.")
    parser.add_argument("-y", "--seedY", type=int, required=True, help="Y coordinate of the seed point.")
    parser.add_argument("-d", "--initial_distance", type=float, required=True, help="Stopping value for fast marching.")
    parser.add_argument("-l", "--lower_threshold", type=float, required=True, help="Lower threshold value for the threshold filter.")
    parser.add_argument("-u", "--upper_threshold", type=float, required=True, help="Upper threshold value for the threshold filter.")

    args = parser.parse_args()

    # Input and output paths
    input_path = './data/BrainProtonDensitySlice.png'
    thresholded_output_path = './output/Threshold/BrainProtonDensitySliceThreshold.png'

    #define input types
    InternalPixelType = itk.F
    Dimension = 2
    InternalImageType = itk.Image[InternalPixelType, Dimension]
    OutputPixelType = itk.UC
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    # Reader
    reader = itk.ImageFileReader[InternalImageType].New()
    reader.SetFileName(input_path)

    # writer
    writer = itk.ImageFileWriter[OutputImageType].New()
    writer.SetFileName(thresholded_output_path)

    # Threshold filter
    threshold = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New()
    threshold.SetLowerThreshold(-1000)
    threshold.SetUpperThreshold(0)
    threshold.SetOutsideValue(0)
    threshold.SetInsideValue(255)

    # Initializing seeds
    NodeContainer = itk.VectorContainer[itk.UI, itk.LevelSetNode[itk.F, Dimension]].New()
    seeds = NodeContainer.New()
    seedPosition = [args.seedX, args.seedY]

    node = itk.LevelSetNode[itk.F, Dimension]()
    node.SetValue(-args.initial_distance)
    node.SetIndex(seedPosition)
    seeds.Initialize()
    seeds.InsertElement(0, node)

    # Fast marching filter
    fast_marching = itk.FastMarchingImageFilter[InternalImageType, InternalImageType].New()
    fast_marching.SetTrialPoints(seeds)
    fast_marching.SetSpeedConstant(1.0)

    # ThresholdSegmentationLevelSetImageFilter
    threshold_segmentation = itk.ThresholdSegmentationLevelSetImageFilter[InternalImageType, InternalImageType, InternalPixelType].New()

    threshold_segmentation.SetPropagationScaling(1.0)
    threshold_segmentation.SetCurvatureScaling(1.0)
    threshold_segmentation.SetUpperThreshold(args.upper_threshold)
    threshold_segmentation.SetLowerThreshold(args.lower_threshold)
    threshold_segmentation.SetIsoSurfaceValue(0.0)
    threshold_segmentation.SetMaximumRMSError(0.02)
    threshold_segmentation.SetNumberOfIterations(1500)

    threshold_segmentation.SetInput(fast_marching.GetOutput())
    threshold_segmentation.SetFeatureImage(reader.GetOutput())
    threshold.SetInput(threshold_segmentation.GetOutput())
    writer.SetInput(threshold.GetOutput())

    try:
        reader.Update()
        input_image = reader.GetOutput()
        fast_marching.SetOutputRegion(input_image.GetBufferedRegion())
        fast_marching.SetOutputSpacing(input_image.GetSpacing())
        fast_marching.SetOutputOrigin(input_image.GetOrigin())
        fast_marching.SetOutputDirection(input_image.GetDirection())
        writer.Update()
        print("Thresholding completed successfully.")
    except Exception as e:
        print("Exception caught while thresholding!", str(e))
        


if __name__ == "__main__":
    main()

