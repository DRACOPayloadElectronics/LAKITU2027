# HSV Color Segmentation and Contour
import cv2
import numpy as np
from time import sleep

def calibrate_hsv_range(image_path):
#   Hue (H): 0 to 179 (The standard 0–360 range is halved to fit under 255)
#   Saturation (S): 0 to 255 (Represents the intensity or purity of the color)
#   Value (V): 0 to 255 (Represents the brightness of the color)
#   HSV_THRESHOLDS = [H,S,V] 

    cv2.namedWindow("HSV Calibration Sliders", cv2.WINDOW_NORMAL)

    title_window = "HSV Calibration Image"
    cv2.namedWindow(title_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title_window, 600, 600)

    original_image = cv2.imread(image_path)
    imgHSV = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

    def update_thresholds(arg):

        hue_upper = cv2.getTrackbarPos("hue_upper", "HSV Calibration Sliders")
        sat_upper = cv2.getTrackbarPos("sat_upper", "HSV Calibration Sliders")
        val_upper = cv2.getTrackbarPos("val_upper", "HSV Calibration Sliders")

        hue_lower = cv2.getTrackbarPos("hue_lower", "HSV Calibration Sliders")
        sat_lower = cv2.getTrackbarPos("sat_lower", "HSV Calibration Sliders")
        val_lower = cv2.getTrackbarPos("val_lower", "HSV Calibration Sliders")

        lower_thresholds = np.array([hue_lower, sat_lower, val_lower])
        upper_thresholds = np.array([hue_upper, sat_upper, val_upper])

        mask = cv2.inRange(imgHSV, lower_thresholds, upper_thresholds)
        color_detected_image = cv2.bitwise_and(original_image, original_image, mask=mask)
        cv2.imshow(title_window, color_detected_image)

    cv2.createTrackbar("hue_lower", "HSV Calibration Sliders" , 0, 179, update_thresholds)
    cv2.createTrackbar("sat_lower", "HSV Calibration Sliders" , 0, 255, update_thresholds)
    cv2.createTrackbar("val_lower", "HSV Calibration Sliders" , 0, 255, update_thresholds)
    cv2.createTrackbar("hue_upper", "HSV Calibration Sliders" , 0, 179, update_thresholds)
    cv2.createTrackbar("sat_upper", "HSV Calibration Sliders" , 0, 255, update_thresholds)
    cv2.createTrackbar("val_upper", "HSV Calibration Sliders" , 0, 255, update_thresholds)

    update_thresholds(0)

    while True:
        if cv2.waitKey(100) == 13:
            cv2.destroyAllWindows()
            return

def capture_frame():
    # Open the default webcam (0)
    cap = cv2.VideoCapture(0)
    
    # Check if the webcam was opened successfully
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
    
    # Read the first frame to confirm capturing
    ret, frame = cap.read()
    
    if ret: 
        return frame
    else:
        print("Error: Could not capture a frame.")
    
    # Release the webcam
    cap.release()

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
    calibrate_hsv_range("Images/hsv_input_image_test1.jpeg")
    # frame_to_process = capture_frame()
    # process_image(frame=None, image_path="Images/hsv_input_image_test1.jpeg", live_frame=False)

if __name__ == "__main__":
    main()