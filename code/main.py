# HSV Color Segmentation and Contour
import cv2
import numpy as np
from picamera2 import Picamera2

def calibrate_hsv_range():
# Camera Initialization
    # Initialize the camera
    picam2 = Picamera2()

    # Configure resolution and color format
    # 'RGB888' outputs 3-channel arrays ready for OpenCV
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    
    picam2.start()
    
#   Hue (H): 0 to 179 (The standard 0–360 range is halved to fit under 255)
#   Saturation (S): 0 to 255 (Represents the intensity or purity of the color)
#   Value (V): 0 to 255 (Represents the brightness of the color)
#   HSV_THRESHOLDS = [H,S,V] 

    cv2.namedWindow("HSV Calibration Sliders", cv2.WINDOW_NORMAL)
    
    thresholds = [np.array([0,0,0]),np.array([179,255,255])]

    def update_thresholds(arg):

        hue_upper = cv2.getTrackbarPos("hue_upper", "HSV Calibration Sliders")
        sat_upper = cv2.getTrackbarPos("sat_upper", "HSV Calibration Sliders")
        val_upper = cv2.getTrackbarPos("val_upper", "HSV Calibration Sliders")

        hue_lower = cv2.getTrackbarPos("hue_lower", "HSV Calibration Sliders")
        sat_lower = cv2.getTrackbarPos("sat_lower", "HSV Calibration Sliders")
        val_lower = cv2.getTrackbarPos("val_lower", "HSV Calibration Sliders")

        lower_thresholds = np.array([hue_lower, sat_lower, val_lower])
        upper_thresholds = np.array([hue_upper, sat_upper, val_upper])
        
        thresholds[0] = lower_thresholds
        thresholds[1] = upper_thresholds
        
        frame = picam2.capture_array()
        
        original_image = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
        imgHSV = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV, thresholds[0], thresholds[1])
        color_detected_image = cv2.bitwise_and(original_image, original_image, mask=mask)
        
        # cv2.imshow("PI CAMERA FEED OG", frame)
        cv2.imshow("Pi Camera Feed", color_detected_image)
        
    cv2.createTrackbar("hue_lower", "HSV Calibration Sliders" , 0, 179, update_thresholds)
    cv2.createTrackbar("sat_lower", "HSV Calibration Sliders" , 0, 255, update_thresholds)
    cv2.createTrackbar("val_lower", "HSV Calibration Sliders" , 0, 255, update_thresholds)
    cv2.createTrackbar("hue_upper", "HSV Calibration Sliders" , 0, 179, update_thresholds)
    cv2.createTrackbar("sat_upper", "HSV Calibration Sliders" , 0, 255, update_thresholds)
    cv2.createTrackbar("val_upper", "HSV Calibration Sliders" , 0, 255, update_thresholds)
    
    while True:
        update_thresholds(0)
        if cv2.waitKey(100) == 13:
            cv2.destroyAllWindows()
            return

def process_image(frame, image_path, live_frame):

    while True:
        # 1. Transform RGB colors into HSV
        if live_frame:
            original_image = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
        else:
            original_image = cv2.imread(image_path)
            
        imgHSV = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        # 2. Define HSV thresholds
        lower = np.array([177, 100, 100])
        upper = np.array([179, 170, 170])

        # 3. Apply masking
        mask = cv2.inRange(imgHSV, lower, upper)
        final_image = cv2.resize(mask, (600,600))
        cv2.imshow("Processed-Image-Test-2", final_image)

        # 4. Clean up (specks removal and gap filling) (still pending)

        ## create color detected image
        color_detected_image = cv2.bitwise_and(original_image, original_image, mask=mask)

        # 5. Define contour
        contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.1 * cv2.arcLength(contour, True), True)

            if len(approx) == 4 and cv2.contourArea(contour) >= 150:
                #print(cv2.contourArea(contour=contour))
                #print(contour)
                final_image = cv2.drawContours(original_image.copy(), contours, -1, (140, 255, 0), 2)
                final_image = cv2.resize(final_image, (600,600))
                
                

        # 6. Output processed image (this is not the finalized result)
        # final_image = cv2.drawContours(color_detected_image.copy(), contours, -1, (140, 255, 0), 2)

        ## Display original, HSV, and masked images
        # cv2.imshow("Original Image", image)
        # cv2.imshow("Processed Image", final_image)
        # cv2.imwrite("output_image_test1.png", final_image)
        # break

        if cv2.waitKey(100) == 13:
            break

    cv2.destroyAllWindows()
    return

def main():
    calibrate_hsv_range()
    # process_image(frame=None, image_path="Images/hsv_input_image_test1.jpeg", live_frame=False)

if __name__ == "__main__":
    main()
