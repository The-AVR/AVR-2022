#include "apriltags.hpp"

uint32_t process_frame(cv::Mat img_rgba8, AprilTagsImpl* impl_)
{

        //copy the image to cuda mem
        const cudaError_t cuda_error =
                cudaMemcpy(impl_->input_image_buffer,
                           (uchar4 *)img_rgba8.ptr<unsigned char>(0),
                           impl_->input_image_buffer_size,
                           cudaMemcpyHostToDevice);
        
        if (cuda_error != cudaSuccess) {
            throw std::runtime_error(
                    "Could not memcpy to device CUDA memory (error code " +
                    std::to_string(cuda_error) + ")");
        }

        //run the detector
        uint32_t num_detections;
        const int error = nvAprilTagsDetect(
            impl_->april_tags_handle,
            &(impl_->input_image), 
            impl_->tags.data(),
            &num_detections, 
            impl_->max_tags, 
            impl_->main_stream
        );

    
        if (error != 0) {
            throw std::runtime_error("Failed to run AprilTags detector (error code " +
                                     std::to_string(error) + ")");
        }
        
        return num_detections;
};