#include <opencv2/core/version.hpp>

#if CV_MAJOR_VERSION >= 3
#include <opencv2/imgcodecs.hpp>
#else
#include <opencv2/highgui/highgui.hpp>
#endif

#include <opencv2/imgproc/imgproc.hpp>
#include <vpi/OpenCVInterop.hpp>

#include <string.h> // for basename(3) that doesn't modify its argument
#include <unistd.h> // for getopt
#include <vpi/Image.h>
#include <vpi/LensDistortionModels.h>
#include <vpi/Status.h>
#include <vpi/Stream.h>
#include <vpi/algo/ConvertImageFormat.h>
#include <vpi/algo/Remap.h>

#include <iostream>
#include <sstream>

#ifndef CAM_PROPERTIES_H
#include "cam_properties.hpp"
#endif

#define CHECK_STATUS(STMT)                                    \
    do                                                        \
    {                                                         \
        VPIStatus status = (STMT);                            \
        if (status != VPI_SUCCESS)                            \
        {                                                     \
            char buffer[VPI_MAX_STATUS_MESSAGE_LENGTH];       \
            vpiGetLastStatusMessage(buffer, sizeof(buffer));  \
            std::ostringstream ss;                            \
            ss << vpiStatusGetName(status) << ": " << buffer; \
            throw std::runtime_error(ss.str());               \
        }                                                     \
    } while (0);

//###################################################################### V P I ####################################################################

// VPI objects that will be used
extern VPIStream stream;
extern VPIPayload remap;
extern VPIImage tmpIn, tmpOut;
extern VPIImage vimg;

// Camera intrinsic parameters, initially identity (will be estimated by calibration process).
using Mat3 = cv::Matx<double, 3, 3>;
extern Mat3 camMatrix;

// Allocate a dense map.
extern VPIWarpMap map;

// Initialize the fisheye lens model with the coefficients given by calibration procedure.
extern VPIFisheyeLensDistortionModel distModel;

void setup_vpi(cv::Mat img_rgba8);

void undistort_frame(cv::Mat frame);