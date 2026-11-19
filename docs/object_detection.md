# Object Detection
This document contains the approaches being considered for object detection

## Object Description
The target will be a 40'x40' pink canvas tarp. The intended target elevation is approximately 80' above ground.

    - Approximate RGB: 242, 119, 144
    - Approximate Hex Color Code: #F27790
    - Approximate HSV: 348, 50.8, 94.9

## Approach 1 - HSV color segmentation and contour

## ALGORITHM (general description)
1. Transform RGB colors into HSV
2. Define HSV thresholds
3. Apply masking
4. Clean up (specks removal and gap filling)
5. Define contour
6. Output processed image (this is not the finalized result)

## What is HSV and contour?
HSV stands for hue (actual color), saturation (how vivid), and value (how bright). It is a better representation for object detection than RGB. 

Contour is basically an outline or delimitation of the area that contains our candidate object.

## HSV Thresholds
The HSV thresholds define the upper and lower limits of the HSV values that should be allowed in our mask. 

This thresholds should be defined thorugh experimentation. Different lightning and distances should be considered when defining this limits (upper and lower).

## What is masking?
Masking refers to the step where we turn every pixel that is outside our HSV thresholds to black and turns the rest (pixels inside the threshold) to white.

# References 
    1. https://docs.opencv.org/5.0
    2. https://medium.com/@VinitKumarGupta/color-detection-in-opencv-a-hands-on-project-to-master-hsv-filtering-5fa9fd928561
    3. https://www.rapidtables.com/convert/color/rgb-to-hsv.html