import itk
import argparse

def rescale_and_write(filter_output, output_image_type, output_path, output_min=0, output_max=255):
    try:
        rescaler = itk.RescaleIntensityImageFilter[type(filter_output), output_image_type].New()
        rescaler.SetInput(filter_output)
        rescaler.SetOutputMinimum(output_min)
        rescaler.SetOutputMaximum(output_max)

        rescaler.Update()

        writer = itk.ImageFileWriter[output_image_type].New()
        writer.SetFileName(output_path)
        writer.SetInput(rescaler.GetOutput())
        writer.Update()

        print(f"{output_path} written successfully.")
    except Exception as e:
        print(f"Exception caught while writing {output_path}!", str(e))


# Argument parser setup with flags
def main():

    parser = argparse.ArgumentParser(description="ITK Geodesic active contour Segmentation with Smoothing, Gradient, and Sigmoid Filters.")

    parser.add_argument("-x", "--seedX", type=int, required=True, help="X coordinate of the seed point.")
    parser.add_argument("-y", "--seedY", type=int, required=True, help="Y coordinate of the seed point.")
    parser.add_argument("-s", "--sigma", type=float, required=True, help="Sigma value for the gradient magnitude filter.")
    parser.add_argument("-a", "--alpha", type=float, required=True, help="Alpha value for the sigmoid filter.")
    parser.add_argument("-b", "--beta", type=float, required=True, help="Beta value for the sigmoid filter.")
    parser.add_argument("-p", "--propagation_scaling", type=float, required=True, help="Time threshold for fast marching.")
    parser.add_argument("-d", "--initial_distance", type=float, required=True, help="Stopping value for fast marching.")

    args = parser.parse_args()

    # Input and output paths
    input_path = './data/BrainProtonDensitySlice.png'
    smoothing_output_path = './output/GeodesicActiveContour/BrainProtonDensitySliceSmoothing.png'
    gradient_output_path = './output/GeodesicActiveContour/BrainProtonDensitySliceGradient.png'
    sigmoid_output_path = './output/GeodesicActiveContour/BrainProtonDensitySliceSigmoid.png'
    fast_marching_output_path = './output/GeodesicActiveContour/BrainProtonDensitySliceFastMarching.png'
    thresholded_output_path = './output/GeodesicActiveContour/BrainProtonDensitySliceGeodesicActiveContour.png'

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

    # Thresholding filter
    thresholder = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New()
    thresholder.SetLowerThreshold(-1000.0)
    thresholder.SetUpperThreshold(0)
    thresholder.SetOutsideValue(0)
    thresholder.SetInsideValue(255)

    # Smoothing filter
    smoothing = itk.CurvatureAnisotropicDiffusionImageFilter[InternalImageType, InternalImageType].New()
    smoothing.SetInput(reader.GetOutput())
    smoothing.SetTimeStep(0.125)
    smoothing.SetNumberOfIterations(5)
    smoothing.SetConductanceParameter(9.0)

    # Gradient magnitude filter
    gradient = itk.GradientMagnitudeRecursiveGaussianImageFilter[InternalImageType, InternalImageType].New()
    gradient.SetInput(smoothing.GetOutput())
    gradient.SetSigma(args.sigma)

    # Sigmoid filter
    sigmoid = itk.SigmoidImageFilter[InternalImageType, InternalImageType].New()
    sigmoid.SetInput(gradient.GetOutput())
    sigmoid.SetAlpha(args.alpha)
    sigmoid.SetBeta(args.beta)
    sigmoid.SetOutputMinimum(0.0)
    sigmoid.SetOutputMaximum(1.0)


    NodeContainer = itk.VectorContainer[itk.UI, itk.LevelSetNode[itk.F, Dimension]].New()
    seeds = NodeContainer.New()
    seedPosition = [args.seedX, args.seedY]

    node = itk.LevelSetNode[itk.F, Dimension]()
    node.SetValue(-args.initial_distance)
    node.SetIndex(seedPosition)
    seeds.Initialize()
    seeds.InsertElement(0, node)

    # Fast Marching filter
    fast_marching = itk.FastMarchingImageFilter[InternalImageType, InternalImageType].New()
    fast_marching.SetInput(sigmoid.GetOutput())
    fast_marching.SetTrialPoints(seeds)
    fast_marching.SetSpeedConstant(1.0)
    fast_marching.SetOutputSize(reader.GetOutput().GetBufferedRegion().GetSize())

    # Geodesic Active Contour filter
    geodesic_active_contour = itk.GeodesicActiveContourLevelSetImageFilter[InternalImageType, InternalImageType, InternalPixelType].New()
    geodesic_active_contour.SetInput(fast_marching.GetOutput())
    geodesic_active_contour.SetFeatureImage(sigmoid.GetOutput())
    geodesic_active_contour.SetPropagationScaling(args.propagation_scaling)
    geodesic_active_contour.SetCurvatureScaling(1.0)
    geodesic_active_contour.SetAdvectionScaling(1.0)
    geodesic_active_contour.SetMaximumRMSError(0.02)
    geodesic_active_contour.SetNumberOfIterations(800)

    # Set the output of the thresholding filter to the writer
    thresholder.SetInput(geodesic_active_contour.GetOutput())
    writer.SetInput(thresholder.GetOutput())


    try:
        rescale_and_write(smoothing.GetOutput(), OutputImageType, smoothing_output_path)
        rescale_and_write(gradient.GetOutput(), OutputImageType, gradient_output_path)
        rescale_and_write(sigmoid.GetOutput(), OutputImageType, sigmoid_output_path)
        rescale_and_write(fast_marching.GetOutput(), OutputImageType, fast_marching_output_path)

        writer.Update()
        print(f"Geodesic Active Contour Segmentation Complete. Output {thresholded_output_path} written successfully.")
    except Exception as e:
        print(f"Exception caught while writing {thresholded_output_path}!", str(e))


    
if __name__ == '__main__':
    main()
