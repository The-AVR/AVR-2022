# AprilTag Module

### What does this module do? 

The apriltag module is responsible for using the images pulled from the CSI camera to scan for visible [apriltags](https://april.eecs.umich.edu/software/apriltag). 

A low-level C++ program captures the images and hands them off to the Jetson's GPU for processing and publishes the raw detections to the "vrc/apriltags/raw" topic. 

From here, a second program, written in python subscribes to this topic, and upon new detections, uses linear algebra to perform a coordinate transformation in order to get several pieces of data. These detections include the tags ID, as well as the drone's absolute location in the court (pos_world), and the drones relative location to the tag itself (pos_rel).

This data is then broadcast out over MQTT for other modules, such as the fusion and sandbox modules to consume.

### MQTT Data:

##### Subscribes: 

This module subscribes to the **"vrc/apriltags/raw"** topic

##### Publishes:

- This module publishes the raw tag data to the **"vrc/apriltags/raw"** topic in the following format:

  - `id` - the id of the tag
  - `pos`
    - `x` - the position **in meters** of the camera relative to the **tag's x** frame
    - `y` - the position **in meters** of the camera relative to the **tag's y** frame
    - `z` - the position **in meters** of the camera relative to the **tag's z** frame
  - `rotation` - the 3x3 rotation matrix 

  Sample Output:

```json
[
    {
        "id": 0, 
        "pos" : {
            "x" : -0.34972984, 
            "y" : 0.024662515, 
            "z" : 1.2223765 
        },
        "rotation": [ 
                [
                    0.01692861,
                    -0.96672946,
                    -0.25524017
                ],
                [
                    0.9984415,
                    0.029921694,
                    -0.0471084
                ],
                [
                    0.0531783,
                    -0.25404492,
                    0.9657294
                ]
        ]
    }
]
```

- This module publishes the transformed tag data to the **"vrc/apriltags/visible_tags"** topic in the following format:

  - `id` - the id of the tag

  - `horizontal_dist` - the horizontal scalar distance from vehicle to tag, **in cm**
  
  - `vertical_dist` - the vertical scalar distance from vehicle to tag, **in cm**
  
  - `angle_to_tag` - the angle formed by the vector pointing from the vehicles body to the tag in world frame relative to world-north
  
  - `heading` -  the heading of the vehicle in world frame
  
  - `pos_rel` - the relative position of the vehicle to the tag in world frame **in cm** 
  
    - `x` -  the x (+north/-south) position of the vehicle relative to the tag in world frame (for reference the mountain is **north** of the beach)
    - `y` - the y (+east/-west) position of the vehicle relative to the tag in world frame
    - `x` - the z (+down/-up) position of the vehicle relative to the tag in world frame (no, this is not a typo, up is really - )
  
  - `pos_world` - the position of the vehicle in world frame **in cm** (if the tag has no truth data, this will not be present in the output)
  
    - `x` - the x position of the vehicle relative to the world origin (this is the ship) in world frame (for reference the mountain is **north** of the beach)
    - `y` - the y position of the vehicle relative to the world origin in world frame
    - `z` - the z position of the vehicle relative to the world origin in world frame

    Sample output:
  
  ```json
  [
    {
        "id": 0, 
        "horizontal_dist": 37.99064257948583, 
        "vertical_dist": 130.41844, 
        "angle_to_tag": 246.93741507324984, 
        "heading": 1.0087819541794854, 
        "pos_rel": { 
            "x": -14.882316594277325, 
            "y": -34.95433558787721, 
            "z": -130.41844 
        }, 
        "pos_world": { 
            "x": -14.882316594277325, 
            "y": -34.95433558787721, 
            "z": -130.41844
        }
    }
  ]
  ```
  
  - This module publishes its best candidate for position feedback on the **"vrc/apriltags/selected"** topic in the following format:
  
    - `tag_id` - the id of the tag
    - `pos` - the position of the vehicle in world frame **in cm**
      - `n` - the +north position of the vehicle relative to the world origin in world frame
      - `e` - the +east position of the vehicle relative to the world origin in world frame
      - `d` - the +down position of the vehicle relative to the world origin in world frame
    - `heading` - the heading of the vehicle in world frame
  
    Sample Output:
  
    ```json
    {
        "tag_id": 0, 
        "pos": {
            "n": -13.170389200935961, 
            "e": -18.131769212308722, 
            "d": -135.12779
        }, 
        "heading": 1.9824482318601353
    }
    ```
  
    
