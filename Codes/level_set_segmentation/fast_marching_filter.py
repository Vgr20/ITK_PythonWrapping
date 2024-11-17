import itk
import argparse

# Utility function for applying a rescaler and writing output to a file
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

def main():
    # Argument parser setup with flags
    parser = argparse.ArgumentParser(description="ITK Fast Marching Segmentation with Smoothing, Gradient, and Sigmoid Filters.")

    parser.add_argument("-x", "--seedX", type=int, required=True, help="X coordinate of the seed point.")
    parser.add_argument("-y", "--seedY", type=int, required=True, help="Y coordinate of the seed point.")
    parser.add_argument("-s", "--sigma", type=float, required=True, help="Sigma value for the gradient magnitude filter.")
    parser.add_argument("-a", "--alpha", type=float, required=True, help="Alpha value for the sigmoid filter.")
    parser.add_argument("-b", "--beta", type=float, required=True, help="Beta value for the sigmoid filter.")
    parser.add_argument("-t", "--time_threshold", type=float, required=True, help="Time threshold for fast marching.")
    parser.add_argument("-q", "--stopping_value", type=float, required=True, help="Stopping value for fast marching.")
    
    args = parser.parse_args()

    # Input and output paths
    input_path = './data/BrainProtonDensitySlice.png'
    output_path = './output/FastMarching/BrainProtonDensitySliceFastMarching.png'
    smoothing_output_path = './output/FastMarching/BrainProtonDensitySliceSmoothing.png'
    gradient_output_path = './output/FastMarching/BrainProtonDensitySliceGradient.png'
    sigmoid_output_path = './output/FastMarching/BrainProtonDensitySliceSigmoid.png'
    thresholded_output_path = './output/FastMarching/Thresholded_BrainProtonDensitySliceFastMarching.png'

    # Internal types and setup
    InternalPixelType = itk.F
    Dimension = 2
    InternalImageType = itk.Image[InternalPixelType, Dimension]
    OutputPixelType = itk.UC
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    # Reader
    reader = itk.ImageFileReader[InternalImageType].New()
    reader.SetFileName(input_path)

    # Thresholding filter
    thresholder = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New()
    thresholder.SetLowerThreshold(0)
    thresholder.SetUpperThreshold(int(args.time_threshold))
    thresholder.SetOutsideValue(0)
    thresholder.SetInsideValue(255)

    # Smoothing filter
    smoothing = itk.CurvatureAnisotropicDiffusionImageFilter[InternalImageType, InternalImageType].New()
    smoothing.SetInput(reader.GetOutput())
    smoothing.SetTimeStep(0.125)
    smoothing.SetNumberOfIterations(5)
    smoothing.SetConductanceParameter(9.0)

    # Gradient filter
    gradientMagnitude = itk.GradientMagnitudeRecursiveGaussianImageFilter[InternalImageType, InternalImageType].New()
    gradientMagnitude.SetInput(smoothing.GetOutput())
    gradientMagnitude.SetSigma(args.sigma)

    # Sigmoid filter
    sigmoid = itk.SigmoidImageFilter[InternalImageType, InternalImageType].New()
    sigmoid.SetInput(gradientMagnitude.GetOutput())
    sigmoid.SetAlpha(args.alpha)
    sigmoid.SetBeta(args.beta)
    sigmoid.SetOutputMinimum(0.0)
    sigmoid.SetOutputMaximum(1.0)

    # Fast marching filter
    fastMarching = itk.FastMarchingImageFilter[InternalImageType, InternalImageType].New()
    fastMarching.SetInput(sigmoid.GetOutput())
    fastMarching.SetOutputSize(reader.GetOutput().GetBufferedRegion().GetSize())
    fastMarching.SetStoppingValue(args.stopping_value)

    # Seed points for Fast Marching
    NodeContainer = itk.VectorContainer[itk.UI, itk.LevelSetNode[itk.F, Dimension]].New()
    seeds = NodeContainer.New()
    seedPosition = [args.seedX, args.seedY]

    node = itk.LevelSetNode[itk.F, Dimension]()
    node.SetValue(0.0)
    node.SetIndex(seedPosition)
    seeds.Initialize()
    seeds.InsertElement(0, node)
    fastMarching.SetTrialPoints(seeds)


    thresholder.SetInput(fastMarching.GetOutput())

    writer = itk.ImageFileWriter[OutputImageType].New()
    writer.SetFileName(thresholded_output_path)
    writer.SetInput(thresholder.GetOutput())

    # Apply filters and write outputs
    smoothing.Update()
    rescale_and_write(smoothing.GetOutput(), OutputImageType, smoothing_output_path)

    gradientMagnitude.Update()
    rescale_and_write(gradientMagnitude.GetOutput(), OutputImageType, gradient_output_path)

    sigmoid.Update()
    rescale_and_write(sigmoid.GetOutput(), OutputImageType, sigmoid_output_path)

    fastMarching.Update()
    rescale_and_write(fastMarching.GetOutput(), OutputImageType, output_path)

    thresholder.Update()
    try:
        writer.Update()
        print(f"{thresholded_output_path} written successfully.")
    except Exception as e:
        print(f"Exception caught while writing {output_path}!", str(e))


if __name__ == "__main__":
    main()

# Run the script with the following command:
# python fast_marching_filter.py --seedX 81 --seedY 114 --sigma 1.0 --alpha -0.5 --beta 3.0 --time_threshold 100 --stopping_value 100
# python fast_marching_filter.py --seedX 99 --seedY 114 --sigma 1.0 --alpha -0.5 --beta 3.0 --time_threshold 100 --stopping_value 100
# python fast_marching_filter.py --seedX 56 --seedY 92 --sigma 1.0 --alpha -0.3 --beta 3.0 --time_threshold 200 --stopping_value 100
# python fast_marching_filter.py --seedX 40 --seedY 90 --sigma 1.0 --alpha -0.3 --beta 3.0 --time_threshold 200 --stopping_value 100
# The output images will be saved in the output directory.
