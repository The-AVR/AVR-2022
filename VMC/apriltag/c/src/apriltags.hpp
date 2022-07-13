#include <opencv2/core/version.hpp>

#if CV_MAJOR_VERSION >= 3
#include <opencv2/imgcodecs.hpp>
#else
#include <opencv2/highgui/highgui.hpp>
#endif

#include <iostream>
#include "../libraries/nvapriltags/nvAprilTags.h"
#include "cuda.h"
#include "cuda_runtime.h"
#include <opencv2/opencv.hpp>
#include <chrono>

#include <opencv2/imgproc/imgproc.hpp>

struct AprilTagsImpl
{
    // Handle used to interface with the stereo library.
    nvAprilTagsHandle april_tags_handle = nullptr;
    // Camera intrinsics
    nvAprilTagsCameraIntrinsics_t cam_intrinsics;

    // Output vector of detected Tags
    std::vector<nvAprilTagsID_t> tags;

    // CUDA stream
    cudaStream_t main_stream = {};

    // CUDA buffers to store the input image.
    nvAprilTagsImageInput_t input_image;

    // CUDA memory buffer container for RGBA images.
    uchar4 *input_image_buffer = nullptr;

    // Size of image buffer
    size_t input_image_buffer_size = 0;

    int max_tags;

    void initialize(const uint32_t width,
                    const uint32_t height,
                    const size_t image_buffer_size,
                    const size_t pitch_bytes,
                    const float fx, const float fy, const float cx, const float cy,
                    float tag_edge_size_, int max_tags_)
    {
        assert(!april_tags_handle), "Already initialized.";

        // Get camera intrinsics
        cam_intrinsics = {fx, fy, cx, cy};

        // Create AprilTags detector instance and get handle
        const int error = nvCreateAprilTagsDetector(
            &april_tags_handle, width, height, nvAprilTagsFamily::NVAT_TAG36H11,
            &cam_intrinsics, tag_edge_size_);
        if (error != 0)
        {
            throw std::runtime_error(
                "Failed to create NV April Tags detector (error code " +
                std::to_string(error) + ")");
        }

        // Create stream for detection
        cudaStreamCreate(&main_stream);

        // Allocate the output vector to contain detected AprilTags.
        tags.resize(max_tags_);
        max_tags = max_tags_;
        // Setup input image CUDA buffer.
        const cudaError_t cuda_error =
            cudaMalloc(&input_image_buffer, image_buffer_size);
        if (cuda_error != cudaSuccess)
        {
            throw std::runtime_error("Could not allocate CUDA memory (error code " +
                                     std::to_string(cuda_error) + ")");
        }

        // Setup input image.
        input_image_buffer_size = image_buffer_size;
        input_image.width = width;
        input_image.height = height;
        input_image.dev_ptr = reinterpret_cast<uchar4 *>(input_image_buffer);
        input_image.pitch = pitch_bytes;
    }

    ~AprilTagsImpl()
    {
        if (april_tags_handle != nullptr)
        {
            cudaStreamDestroy(main_stream);
            nvAprilTagsDestroy(april_tags_handle);
            cudaFree(input_image_buffer);
        }
    }
};

uint32_t process_frame(cv::Mat img_rgba8, AprilTagsImpl *impl_);