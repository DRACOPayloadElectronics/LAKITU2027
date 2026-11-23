# HSV Color Segmentation and Contour
import cv2
import numpy as np
from picamera2 import Picamera2

class ObjectDetector():
    '''
    lower: lower hsv threshold \n
    upper: upper hsv threshold
    '''
    # Thresholds
    lowerThreshold= np.array([0,0,0])
    upperThreshold = np.array([179,255,255])

    # Camera Initialization
    picam2 = Picamera2()

    def __init__(self, lower: list[int], upper: list[int]):
        self.lowerThreshold = np.array(lower)
        self.upperThreshold = np.array(upper)

        # Configure resolution and color format
        # 'RGB888' outputs 3-channel arrays ready for OpenCV
        config = self.picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
        self.picam2.configure(config)

    def calibrateHSVRange(self):
        
        self.picam2.start()
        
    #   Hue (H): 0 to 179 (The standard 0–360 range is halved to fit under 255)
    #   Saturation (S): 0 to 255 (Represents the intensity or purity of the color)
    #   Value (V): 0 to 255 (Represents the brightness of the color)
    #   HSV-THRESHOLDS = [H,S,V] 

        cv2.namedWindow("HSV Calibration Sliders", cv2.WINDOW_NORMAL)

        def updateThreshold(arg):

            hue_upper = cv2.getTrackbarPos("hue_upper", "HSV Calibration Sliders")
            sat_upper = cv2.getTrackbarPos("sat_upper", "HSV Calibration Sliders")
            val_upper = cv2.getTrackbarPos("val_upper", "HSV Calibration Sliders")

            hue_lower = cv2.getTrackbarPos("hue_lower", "HSV Calibration Sliders")
            sat_lower = cv2.getTrackbarPos("sat_lower", "HSV Calibration Sliders")
            val_lower = cv2.getTrackbarPos("val_lower", "HSV Calibration Sliders")

            self.lowerThreshold = np.array([hue_lower, sat_lower, val_lower])
            self.upperThreshold = np.array([hue_upper, sat_upper, val_upper])
            
            frame = self.picam2.capture_array()
            
            original_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
            frameHSV = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HSV)
            maskedFrame = cv2.inRange(frameHSV, self.lowerThreshold, self.upperThreshold)
            
            # cv2.imshow("PI CAMERA FEED OG", frame)
            cv2.imshow("Pi Camera Feed", maskedFrame)
            
        cv2.createTrackbar("hue_lower", "HSV Calibration Sliders" , 0, 179, updateThreshold)
        cv2.createTrackbar("sat_lower", "HSV Calibration Sliders" , 0, 255, updateThreshold)
        cv2.createTrackbar("val_lower", "HSV Calibration Sliders" , 0, 255, updateThreshold)
        cv2.createTrackbar("hue_upper", "HSV Calibration Sliders" , 0, 179, updateThreshold)
        cv2.createTrackbar("sat_upper", "HSV Calibration Sliders" , 0, 255, updateThreshold)
        cv2.createTrackbar("val_upper", "HSV Calibration Sliders" , 0, 255, updateThreshold)
        
        while True:
            updateThreshold(0)
            if cv2.waitKey(100) == 13:
                cv2.destroyAllWindows()
                return

    def processFrame(self, frame):
        # Clean up (specks removal and gap filling) (still pending)

        original_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
        frameHSV = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(frameHSV, self.lowerThreshold, self.upperThreshold)

        # 5. Define contour
        contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.1 * cv2.arcLength(contour, True), True)

            if len(approx) == 4 and cv2.contourArea(contour) >= 150:
                processed_frame = cv2.drawContours(mask.copy(), contours, -1, (140, 255, 0), 2)

        cv2.destroyAllWindows()
        return

def main():
    objectDetection = ObjectDetector([0,0,0],[179,255,255]) 
    objectDetection.calibrateHSVRange()      

main()