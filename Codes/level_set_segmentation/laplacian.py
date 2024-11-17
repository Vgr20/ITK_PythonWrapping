import itk
import argparse

# Argument parser setup with flags
def main():
    parser = argparse.ArgumentParser(description="ITK Geodesic active contour Segmentation with Smoothing, Gradient, and Sigmoid Filters.")
    parser.add_argument("-i", "--diffusion_iterations", type=int, required=True, help="Number of iterations for the diffusion filter.")
    parser.add_argument("-c", "--conductance", type=float, required=True, help="Conductance value for the diffusion filter.")
    parser.add_argument("-p", "--propagation_weight", type=float, required=True, help="Propagation weight for the geodesic active contour filter.")
    parser.add_argument("-m", "--initial_model_isovalued", type=float, required=True, help="Isovalue for the initial model.")
    parser.add_argument("-t", "--iterations", type=int, required=True, help="Number of iterations for the geodesic active contour filter.")

    args = parser.parse_args()

    # Input and output paths
    input_path = './data/BrainProtonDensitySlice.png'
    model_path = './data/VentricleModel.png'
    output_path = './output/Laplacian/BrainProtonDensitySliceLaplacian.png'

    #define input types
    InternalPixelType = itk.F
    Dimension = 2
    InternalImageType = itk.Image[InternalPixelType, Dimension]
    OutputPixelType = itk.UC
    OutputImageType = itk.Image[OutputPixelType, Dimension]

    # Reader
    reader1 = itk.ImageFileReader[InternalImageType].New()
    reader1.SetFileName(input_path)

    reader2 = itk.ImageFileReader[InternalImageType].New()
    reader2.SetFileName(model_path)

    # writer
    writer = itk.ImageFileWriter[OutputImageType].New()
    writer.SetFileName(output_path)

    # Threshold filter
    threshold = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New()
    threshold.SetLowerThreshold(0)
    threshold.SetUpperThreshold(10)
    threshold.SetOutsideValue(0)
    threshold.SetInsideValue(255)

    # Diffusion filter
    diffusion = itk.GradientAnisotropicDiffusionImageFilter[InternalImageType, InternalImageType].New()
    diffusion.SetNumberOfIterations(args.diffusion_iterations)
    diffusion.SetTimeStep(0.125)
    diffusion.SetConductanceParameter(args.conductance)
    diffusion.SetInput(reader1.GetOutput())

    # LaplacianSegmentationLevelSetImageFilterType filter
    laplacian = itk.LaplacianSegmentationLevelSetImageFilter[InternalImageType, InternalImageType,InternalPixelType].New()
    laplacian.SetCurvatureScaling(1.0)
    laplacian.SetPropagationScaling(args.propagation_weight)
    laplacian.SetMaximumRMSError(0.002)
    laplacian.SetNumberOfIterations(args.iterations)
    laplacian.SetIsoSurfaceValue(args.initial_model_isovalued)
    laplacian.SetInput(reader2.GetOutput())
    laplacian.SetFeatureImage(diffusion.GetOutput())

    threshold.SetInput(laplacian.GetOutput())
    writer.SetInput(threshold.GetOutput())

    try:
        writer.Update()
        print(f"{output_path} written successfully.")
    except Exception as e:
        print(f"Exception caught while writing {output_path}!", str(e))


    

if __name__ == '__main__':
    main()
