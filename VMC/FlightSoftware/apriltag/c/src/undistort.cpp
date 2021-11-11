#include "undistort.hpp"

// VPI objects that will be used
VPIStream stream = NULL;
VPIPayload remap = NULL;
VPIImage tmpIn = NULL, tmpOut = NULL;
VPIImage vimg = nullptr;

// Camera intrinsic parameters, initially identity (will be estimated by calibration process).
using Mat3 = cv::Matx<double, 3, 3>;
Mat3 camMatrix = Mat3::eye();

// Allocate a dense map.
VPIWarpMap map = {};

// Initialize the fisheye lens model with the coefficients given by calibration procedure.
VPIFisheyeLensDistortionModel distModel = {};

void setup_vpi(cv::Mat img_rgba8)
{
    camMatrix(0, 0) = (double)fx;
    camMatrix(1, 1) = (double)fy;
    camMatrix(0, 2) = (double)ppx;
    camMatrix(1, 2) = (double)ppy;

    map.grid.numHorizRegions = 1;
    map.grid.numVertRegions = 1;
    map.grid.regionWidth[0] = img_rgba8.cols;
    map.grid.regionHeight[0] = img_rgba8.rows;
    map.grid.horizInterval[0] = 1;
    map.grid.vertInterval[0] = 1;
    CHECK_STATUS(vpiWarpMapAllocData(&map));

    distModel.mapping = VPI_FISHEYE_EQUIDISTANT;
    distModel.k1 = -0.013826167055651659;
    distModel.k2 = -0.11999744016996756;
    distModel.k3 = 0.2825695466585381;
    distModel.k4 = -0.22616481734332383;

    // Fill up the camera intrinsic parameters given by camera calibration procedure.
    VPICameraIntrinsic K;
    for (int i = 0; i < 2; ++i)
    {
        for (int j = 0; j < 3; ++j)
        {
            K[i][j] = camMatrix(i, j);
        }
    }

    // Camera extrinsics is be identity.
    VPICameraExtrinsic X = {};
    X[0][0] = X[1][1] = X[2][2] = 1;

    // Generate a warp map to undistort an image taken from fisheye lens with
    // given parameters calculated above.
    vpiWarpMapGenerateFromFisheyeLensDistortionModel(K, X, K, &distModel, &map);

    // Create the Remap payload for undistortion given the map generated above.
    CHECK_STATUS(vpiCreateRemap(VPI_BACKEND_CUDA, &map, &remap));

    // Now that the remap payload is created, we can destroy the warp map.
    vpiWarpMapFreeData(&map);

    // Create a stream where operations will take place. We're using CUDA
    // processing.
    CHECK_STATUS(vpiStreamCreate(VPI_BACKEND_CUDA, &stream));

    // Temporary input and output images in NV12 format.
    CHECK_STATUS(vpiImageCreate(1280, 720, VPI_IMAGE_FORMAT_NV12_ER, 0, &tmpIn));
    CHECK_STATUS(vpiImageCreate(1280, 720, VPI_IMAGE_FORMAT_NV12_ER, 0, &tmpOut));
};

void undistort_frame(cv::Mat frame)

{
    ///////////////////////////////// UNDISTORT THE FRAME ////////////////////////////////////////////
    // Wrap it into a VPIImage
    if (vimg == nullptr)
    {
        // Now create a VPIImage that wraps it.
        CHECK_STATUS(vpiImageCreateOpenCVMatWrapper(frame, 0, &vimg));
    }
    else
    {
        CHECK_STATUS(vpiImageSetWrappedOpenCVMat(vimg, frame));
    }

    // Convert BGR -> NV12
    CHECK_STATUS(vpiSubmitConvertImageFormat(stream, VPI_BACKEND_CUDA, vimg, tmpIn, NULL));

    // Undistorts the input image.
    CHECK_STATUS(vpiSubmitRemap(stream, VPI_BACKEND_CUDA, remap, tmpIn, tmpOut, VPI_INTERP_CATMULL_ROM,
                                VPI_BORDER_ZERO, 0));

    // Convert the result NV12 back to BGR, writing back to the input image.
    CHECK_STATUS(vpiSubmitConvertImageFormat(stream, VPI_BACKEND_CUDA, tmpOut, vimg, NULL));

    // Wait until conversion finishes.
    CHECK_STATUS(vpiStreamSync(stream));
    /////////////////////////////////////////////////////////////////////////////////////////////////////
};