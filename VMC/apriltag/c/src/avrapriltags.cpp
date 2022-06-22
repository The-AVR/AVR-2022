#include <string.h> // for basename(3) that doesn't modify its argument
#include <unistd.h> // for getopt
#include <sstream>

#include "cam_properties.hpp"

#include "apriltags.hpp"
#include "undistort.hpp"

#include <nlohmann/json.hpp>

#include "mqtt/client.h"

// for convenience
using json = nlohmann::basic_json<std::map, std::vector, std::string, bool, std::int64_t, std::uint64_t, float>;

json jsonify_tag(nvAprilTagsID_t detection)
{
    // create an empty structure (null)
    json j;

    j["id"] = detection.id;

    j["pos"]["x"] = detection.translation[0];
    j["pos"]["y"] = detection.translation[1];
    j["pos"]["z"] = detection.translation[2];

    j["rotation"] = {{detection.orientation[0], detection.orientation[3], detection.orientation[6]},
                     {detection.orientation[1], detection.orientation[4], detection.orientation[7]},
                     {detection.orientation[2], detection.orientation[5], detection.orientation[8]}};

    return j;
}

int main()
{
    //############################################# SETUP MQTT ####################################################################################
    const std::string SERVER_ADDRESS{"tcp://mqtt:18830"};
    const std::string CLIENT_ID{"nvapriltags"};
    const std::string TAG_TOPIC{"avr/apriltags/raw"};
    const std::string FPS_TOPIC{"avr/apriltags/fps"};

    const int QOS = 0;
    mqtt::client client(SERVER_ADDRESS, CLIENT_ID);

    mqtt::connect_options connOpts;
    connOpts.set_keep_alive_interval(20);
    connOpts.set_clean_session(true);

    try
    {
        std::cout << "\nConnecting..." << std::endl;
        client.connect(connOpts);
        std::cout << "...OK" << std::endl;
    }
    catch (const mqtt::exception &exc)
    {
        std::cerr << exc.what() << std::endl;
        return 1;
    }

    //############################################# SETUP VIDEO CAPTURE ##################################################################################################
    cv::VideoCapture capture("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720,format=NV12, framerate=15/1 ! nvvidconv ! video/x-raw,format=BGRx !  videoconvert ! videorate ! video/x-raw,format=BGR,framerate=5/1 ! appsink", cv::CAP_GSTREAMER);
    std::cout << "made it past cap device" << std::endl;

    cv::Mat frame;
    cv::Mat img_rgba8;

    //capture a frame and hand it to VPI to initialize it
    capture.read(frame);
    cv::cvtColor(frame, img_rgba8, cv::COLOR_BGR2RGBA);
    setup_vpi(img_rgba8);

    //create the apriltag handler
    auto *impl_ = new AprilTagsImpl();
    impl_->initialize(img_rgba8.cols, img_rgba8.rows,
                      img_rgba8.total() * img_rgba8.elemSize(), img_rgba8.step,
                      fx, fy, ppx, ppy, //camera params
                      0.174,            //tag edge length
                      6);               //max number of tags

    //################################################################### MAIN LOOP ##########################################################################################
    while (capture.isOpened())
    {

        auto start = std::chrono::system_clock::now();

        //capture a frame
        bool result = capture.read(frame);
        if (result)
        {
            //undistort it
            undistort_frame(frame);

            //convert the frame to rgba
            cv::cvtColor(frame, img_rgba8, cv::COLOR_BGR2RGBA);

            //send the frame to GPU memory and run the detections
            uint32_t num_detections = process_frame(img_rgba8, impl_);

            std::string payload = "\"tags\":{[";

            //handle the detections
            for (int i = 0; i < num_detections; i++)
            {
                const nvAprilTagsID_t &detection = impl_->tags[i];

                json j = jsonify_tag(detection);

                payload.append(j.dump());
                if (i < num_detections - 1)
                {
                    payload.append(",");
                }
            }

            payload.append("]}");

            auto end = std::chrono::system_clock::now();

            if (num_detections > 0)
            {
                const char *const_payload = payload.c_str();
                client.publish(TAG_TOPIC, const_payload, strlen(const_payload));
            }

            int fps = int(1000 / (std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() + 1));

            std::string fps_str = "{\"fps\": " + std::to_string(fps) + "}";
            const char *const_fps_str = fps_str.c_str();

            client.publish(FPS_TOPIC, const_fps_str, strlen(const_fps_str));
        }
    }
    delete (impl_);
    return 0;
}

// while(capture.isOpened())
// {
//     std::cout<<"while"<<std::endl;
//     capture.read(frame);
//     cv::namedWindow("frame", 0);
//     cv::resizeWindow("frame", 1280,720);
//     cv::imshow("frame", frame);
//     if (cv::waitKey(1)==27)
//         break;
// }