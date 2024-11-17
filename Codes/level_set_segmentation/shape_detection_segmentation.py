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

def main():
    parser = argparse.ArgumentParser(description="ITK Shape Detection Segmentation with Smoothing, Gradient, and Sigmoid Filters.")
    parser.add_argument("-x", "--seedX", type=int, required=True, help="X coordinate of the seed point.")
    parser.add_argument("-y", "--seedY", type=int, required=True, help="Y coordinate of the seed point.")
    parser.add_argument("-d", "--initial_distance", type=float, required=True, help="Initial distance for shape detection segmentation.")
    parser.add_argument("-s", "--sigma", type=float, required=True, help="Sigma value for the gradient magnitude filter.")
    parser.add_argument("-a", "--alpha", type=float, required=True, help="Alpha value for the sigmoid filter.")
    parser.add_argument("-b", "--beta", type=float, required=True, help="Beta value for the sigmoid filter.")
    parser.add_argument("-p", "--propagation_scaling", type=float, required=True, help="Propagation scaling for shape detection segmentation.")
    parser.add_argument("-c", "--curvature_scaling", type=float, required=True, help="Curvature scaling for shape detection segmentation.")

    args = parser.parse_args()

    input_path = './data/BrainProtonDensitySlice.png'
    smoothing_output_path = './output/ShapeDetection/BrainProtonDensitySliceSmoothing.png'
    gradient_output_path = './output/ShapeDetection/BrainProtonDensitySliceGradient.png'
    sigmoid_output_path = './output/ShapeDetection/BrainProtonDensitySliceSigmoid.png'
    fast_marching_output_path = './output/ShapeDetection/BrainProtonDensitySliceFastMarching.png'
    thresholded_output_path = './output/ShapeDetection/Thresholded_BrainProtonDensitySliceShapeDetection.png'

    InternalPixelType = itk.F
    Dimension = 2
    InternalImageType = itk.Image[InternalPixelType, Dimension]
    OutputPixelType = itk.UC
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    reader = itk.ImageFileReader[InternalImageType].New()
    reader.SetFileName(input_path)
    writer = itk.ImageFileWriter[OutputImageType].New()
    writer.SetFileName(thresholded_output_path)

    thresholder = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New()
    thresholder.SetLowerThreshold(-1000.00)
    thresholder.SetUpperThreshold(0)
    thresholder.SetOutsideValue(0)
    thresholder.SetInsideValue(255)

    smoothing = itk.CurvatureAnisotropicDiffusionImageFilter[InternalImageType, InternalImageType].New()
    smoothing.SetInput(reader.GetOutput())
    smoothing.SetTimeStep(0.125)
    smoothing.SetNumberOfIterations(5)
    smoothing.SetConductanceParameter(9.0)

    gradient = itk.GradientMagnitudeRecursiveGaussianImageFilter[InternalImageType, InternalImageType].New()
    gradient.SetInput(smoothing.GetOutput())
    gradient.SetSigma(args.sigma)

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
    node.SetValue(-args.initial_distance)  # Make this positive
    node.SetIndex(seedPosition)
    seeds.Initialize()
    seeds.InsertElement(0, node)

    fast_marching = itk.FastMarchingImageFilter[InternalImageType, InternalImageType].New()
    fast_marching.SetInput(sigmoid.GetOutput())
    fast_marching.SetTrialPoints(seeds)
    fast_marching.SetSpeedConstant(1.0)
    fast_marching.SetOutputSize(reader.GetOutput().GetBufferedRegion().GetSize())

    shape_detection = itk.ShapeDetectionLevelSetImageFilter[InternalImageType, InternalImageType, InternalPixelType].New()
    shape_detection.SetInput(fast_marching.GetOutput())
    shape_detection.SetFeatureImage(sigmoid.GetOutput())  # Ensure FeatureImage is set correctly
    shape_detection.SetPropagationScaling(args.propagation_scaling)
    shape_detection.SetCurvatureScaling(args.curvature_scaling)
    shape_detection.SetMaximumRMSError(0.02)
    shape_detection.SetNumberOfIterations(800)

    thresholder.SetInput(shape_detection.GetOutput())
    writer.SetInput(thresholder.GetOutput())

    try:
        rescale_and_write(smoothing.GetOutput(), OutputImageType, smoothing_output_path)
        rescale_and_write(gradient.GetOutput(), OutputImageType, gradient_output_path)
        rescale_and_write(sigmoid.GetOutput(), OutputImageType, sigmoid_output_path)
        rescale_and_write(fast_marching.GetOutput(), OutputImageType, fast_marching_output_path)


        writer.Update()
        print(f"Shape detection segmentation complete. Output written to {thresholded_output_path}.")
    except Exception as e:
        print(f"Exception caught while writing {thresholded_output_path}!", str(e))

if __name__ == "__main__":
    main()


# The code snippet above is a Python script that uses ITK to perform shape detection segmentation on a brain MRI image. The script reads an input image, applies a series of filters (smoothing, gradient, sigmoid), and then uses the Fast Marching and Shape Detection filters to segment the image based on a seed point. The output is written to a file for visualization and analysis.

# Run the script with the following command:
# python shape_detection_segmentation.py --seedX 100 --seedY 100 --initial_distance 5 --sigma 1.0 --alpha 1.0 --beta 1.0 --propagation_scaling 1.0 --curvature_scaling 1.0




    
