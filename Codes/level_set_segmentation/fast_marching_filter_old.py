import itk
import argparse

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
    output_path = './output/BrainProtonDensitySliceFastMarching.png'
    smoothing_output_path = './output/BrainProtonDensitySliceSmoothing.png'
    gradient_output_path = './output/BrainProtonDensitySliceGradient.png'
    sigmoid_output_path = './output/BrainProtonDensitySliceSigmoid.png'

    # Internal types and setup
    InternalPixelType = itk.F
    Dimension = 2
    InternalImageType = itk.Image[InternalPixelType, Dimension]
    OutputPixelType = itk.UC
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    # Reader and writer
    reader = itk.ImageFileReader[InternalImageType].New()
    reader.SetFileName(input_path)
    writer = itk.ImageFileWriter[OutputImageType].New()
    writer.SetFileName(output_path)

    # Thresholding filter
    thresholder = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New()
    thresholder.SetLowerThreshold(0)
    thresholder.SetUpperThreshold(int(args.time_threshold))
    thresholder.SetOutsideValue(0)
    thresholder.SetInsideValue(255)

    # Smoothing filter
    smoothing = itk.CurvatureAnisotropicDiffusionImageFilter[InternalImageType, InternalImageType].New()
    gradientMagnitude = itk.GradientMagnitudeRecursiveGaussianImageFilter[InternalImageType, InternalImageType].New()
    sigmoid = itk.SigmoidImageFilter[InternalImageType, InternalImageType].New()

    sigmoid.SetOutputMinimum(0.0)
    sigmoid.SetOutputMaximum(1.0)

    # Fast marching filter
    fastMarching = itk.FastMarchingImageFilter[InternalImageType, InternalImageType].New()

    # Connecting the pipeline
    smoothing.SetInput(reader.GetOutput())
    gradientMagnitude.SetInput(smoothing.GetOutput())
    sigmoid.SetInput(gradientMagnitude.GetOutput())
    fastMarching.SetInput(sigmoid.GetOutput())
    thresholder.SetInput(fastMarching.GetOutput())
    writer.SetInput(thresholder.GetOutput())

    smoothing.SetTimeStep(0.125)
    smoothing.SetNumberOfIterations(5)
    smoothing.SetConductanceParameter(9.0)

    # Gradient filter sigma
    gradientMagnitude.SetSigma(args.sigma)

    # Sigmoid parameters
    sigmoid.SetAlpha(args.alpha)
    sigmoid.SetBeta(args.beta)

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

    try:
        # Update the smoothing filter to process the input
        smoothing.Update()

        # Use RescaleIntensityImageFilter to adjust intensity values
        rescaler = itk.RescaleIntensityImageFilter[InternalImageType, OutputImageType].New()
        rescaler.SetInput(smoothing.GetOutput())
        rescaler.SetOutputMinimum(0)
        rescaler.SetOutputMaximum(255)
        
        # Update the rescaler to process the output
        rescaler.Update()

        # Write the rescaled output
        smoothingOutputWriter = itk.ImageFileWriter[OutputImageType].New()
        smoothingOutputWriter.SetFileName(smoothing_output_path)
        smoothingOutputWriter.SetInput(rescaler.GetOutput())
        
        print("smoothing works")
        smoothingOutputWriter.Update()
    except Exception as e:
        print("Exception caught while writing smoothing output!", str(e))
        return

    try:
        gradientMagnitude.Update()

        rescaler = itk.RescaleIntensityImageFilter[InternalImageType, OutputImageType].New()
        rescaler.SetInput(gradientMagnitude.GetOutput())
        rescaler.SetOutputMinimum(0)
        rescaler.SetOutputMaximum(255)

        rescaler.Update()

        gradientOutputWriter = itk.ImageFileWriter[OutputImageType].New()
        gradientOutputWriter.SetFileName(gradient_output_path)
        gradientOutputWriter.SetInput(rescaler.GetOutput())
        print("gradient works")
        gradientOutputWriter.Update()

    except Exception as e:
        print("Exception caught while writing gradient output!", str(e))
        return

    try:
        sigmoid.Update()

        rescaler = itk.RescaleIntensityImageFilter[InternalImageType, OutputImageType].New()
        rescaler.SetInput(sigmoid.GetOutput())
        rescaler.SetOutputMinimum(0)
        rescaler.SetOutputMaximum(255)

        rescaler.Update()

        sigmoidOutputWriter = itk.ImageFileWriter[OutputImageType].New()
        sigmoidOutputWriter.SetFileName(sigmoid_output_path)
        sigmoidOutputWriter.SetInput(rescaler.GetOutput())
        print("sigmoid works")
        sigmoidOutputWriter.Update()
    except Exception as e:
        print("Exception caught while writing sigmoid output!", str(e))
        return

    fastMarching.SetOutputSize(reader.GetOutput().GetBufferedRegion().GetSize())
    fastMarching.SetStoppingValue(args.stopping_value)

    try:
        writer.Update()
        print("fast marching works")
    except Exception as e:
        print("Exception caught while writing final output!", str(e))
        return


    # try:
    #     fastMarching.Update()
    #     mapWriter = itk.ImageFileWriter[OutputImageType].New()
    #     mapWriter.SetFileName("FastMarchingFilterOutput4.mha")
    #     mapWriter.SetInput(fastMarching.GetOutput())
    #     mapWriter.Update()
    #
    #     speedWriter = itk.ImageFileWriter.New(Input=InternalImageType)
    #     speedWriter.SetFileName("FastMarchingFilterOutput3.mha")
    #     speedWriter.SetInput(sigmoid.GetOutput())
    #     speedWriter.Update()
    #
    #     gradientWriter = itk.ImageFileWriter.New(Input=InternalImageType)
    #     gradientWriter.SetFileName("FastMarchingFilterOutput2.mha")
    #     gradientWriter.SetInput(gradientMagnitude.GetOutput())
    #     gradientWriter.Update()
    # except Exception as e:
    #     print("Exception caught while writing additional outputs!", str(e))
    #     return

if __name__ == "__main__":
    main()
