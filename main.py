import numpy as np
import time
from PIL import ImageGrab
import cv2
from IPython.display import Image
import pyautogui
from directkeys import PressKey, W, A, S, D

def draw_lanes(img, lines, color=[0, 200, 0], thickness=3):

    if lines is not None:

        imG = np.copy(img)
        line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8,)
        # Loop over all lines and draw them on the blank image.
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_img, (x1, y1), (x2, y2), color, thickness)

        img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)
        return(img)
    else:
        return

def draw_lines(img,lines):
    try:
        for line in lines:
            coords = line[0]
            cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), [255,255,255], 3)
    except:
        pass

def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return(masked)

def image_process(image):
    originalImage = image

    processedImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processedImage =  cv2.Canny(processedImage, threshold1 = 100, threshold2=300)
    cv2.imwrite('pre.png', processedImage)
    # For 3rd person vertices = np.array([[200,1000],[150,450],[400,225],[800,225],[850,450],[850,700],], np.int32)
    #From hood of car
    vertices = np.array([[10,600],[50,500],[400,160],[600,160],[815,500],[850,600],], np.int32)
    processedImage = cv2.GaussianBlur(processedImage,(5,5),0)
    processedImage = roi(processedImage, [vertices])

    lines = cv2.HoughLinesP(processedImage, 1, np.pi/180, 180, 20, 15)
    draw_lines(processedImage,lines)




    line_image = draw_lanes(originalImage, lines)

    return(line_image)


def screen_record():

    last_time = time.time()
    while True:
        #PressKey(W)
        printscreen =  np.array(ImageGrab.grab(bbox=(0,40,1024,768)))
        new_screen = image_process(printscreen)
        cv2.imwrite('processedImage.png', new_screen)
        num_seconds = time.time() - last_time
        print(num_seconds)
        if num_seconds > 3:
            break
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     cv2.destroyAllWindows()
        #     break

def main():
    for i in range(3,0,-1):
        print(i)
        time.sleep(1)

    screen_record()

if __name__ == "__main__":
    main()
