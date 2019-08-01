import numpy as np
import time
from PIL import ImageGrab
import cv2
from IPython.display import Image
import pyautogui
from directkeys import PressKey, W, A, S, D
import math

def mathfunc(x1,y1,x2,y2):

    slope = (y2-y1)/(x2-x1)
    intercept = y1 - slope*x1
    line_length = np.sqrt((y2-y1)**2+(x2-x1)**2)
    return(slope,intercept,line_length)

def to_keep_index(obs, std=1.5):
    return np.array(abs(obs - np.mean(obs)) < std*np.std(obs))

def avg_lines(image,lines):

    neg = np.empty([1,3])
    pos = np.empty([1,3])

    ## calculate slopes for each line to identify the positive and negative lines
    for line in lines:
        for x1,y1,x2,y2 in line:
            slope,intercept,line_length = mathfunc(x1,y1,x2,y2)
            if slope < 0 and line_length > 10:
                neg = np.append(neg,np.array([[slope, intercept, line_length]]),axis = 0)
            elif slope > 0 and line_length > 10:
                pos = np.append(pos,np.array([[slope, intercept, line_length]]),axis = 0)

    ## just keep the observations with slopes with 2 std dev
    neg = neg[to_keep_index(neg[:,0])]
    pos = pos[to_keep_index(pos[:,0])]

    ## weighted average of the slopes and intercepts based on the length of the line segment
    neg_lines = np.dot(neg[1:,2],neg[1:,:2])/np.sum(neg[1:,2]) if len(neg[1:,2]) > 0 else None
    pos_lines = np.dot(pos[1:,2],pos[1:,:2])/np.sum(pos[1:,2]) if len(pos[1:,2]) > 0 else None

    AvgPositiveM  = pos_lines[0]
    AvgLeftB      = pos_lines[1]
    AvgNegitiveM  = neg_lines[0]
    AvgRightB     = neg_lines[1]

    imshape = image.shape
    y_max   = imshape[0] # lines initial point at bottom of image
    y_min   = 200

    x1_Left = (y_max - AvgLeftB)/AvgPositiveM
    y1_Left = y_max
    x2_Left = (y_min - AvgLeftB)/AvgPositiveM
    y2_Left = y_min

    x1_Right = (y_max - AvgRightB)/AvgNegitiveM
    y1_Right = y_max
    x2_Right = (y_min - AvgRightB)/AvgNegitiveM
    y2_Right = y_min

    # define average left and right lines
    cv2.line(image, (int(x1_Left), int(y1_Left)), (int(x2_Left), int(y2_Left)), [0,200,0], 10) #avg Left Line
    cv2.line(image, (int(x1_Right), int(y1_Right)), (int(x2_Right), int(y2_Right)), [0,200,0], 10) #avg Right Line


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

    # For 3rd person vertices = np.array([[200,1000],[150,450],[400,225],[800,225],[850,450],[850,700],], np.int32)
    #From hood of car
    #vertices = np.array([[10,650],[100,500],[400,200],[625,200],[815,500],[850,650],], np.int32)
    vertices = np.array([[433,383],[30,675],[25,650],[440,220],[610,200],[1000,630],[720,675],[615,380],], np.int32)
    processedImage = cv2.GaussianBlur(processedImage,(5,5),0)
    processedImage = roi(processedImage, [vertices])

    lines = cv2.HoughLinesP(processedImage, 1, np.pi/180, 180, 20, 15)

    draw_lines(processedImage,lines)
    cv2.imwrite('pre.png', processedImage)

    line_image = draw_lanes(originalImage, lines)
    avg_lines(originalImage, lines)


    return(originalImage)


def screen_record():

    last_time = time.time()
    while True:
        #PressKey(W)
        printscreen =  np.array(ImageGrab.grab(bbox=(0,40,1024,768)))
        new_screen = image_process(printscreen)
        cv2.imwrite('processedImage.png', new_screen)
        num_seconds = time.time() - last_time
        print(num_seconds)
        if num_seconds > 2:
            break
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     cv2.destroyAllWindows()
        #     break

def main():
    for i in range(2,0,-1):
        print(i)
        time.sleep(1)

    screen_record()

if __name__ == "__main__":
    main()
