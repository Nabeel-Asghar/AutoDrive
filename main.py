import numpy as np
import time
from PIL import ImageGrab
import cv2
from IPython.display import Image
import pyautogui
from directkeys import ReleaseKey,PressKey, W, A, S, D
from grabscreen import grab_screen
import math
from collections import deque
import statistics

leftSlope = deque()
leftIntercept = deque()

rightSlope= deque()
rightIntercept = deque()

def goStraight():
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(S)
    print("Straight")

def turnLeft():
    PressKey(A)
    time.sleep(2)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(W)
    ReleaseKey(S)
    print("Left")

def turnRight():
    PressKey(D)
    time.sleep(2)
    ReleaseKey(D)
    ReleaseKey(A)
    ReleaseKey(W)
    ReleaseKey(S)
    print("Right")

def rolling_stop():
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    print("Stop")

def mathfunc(x1,y1,x2,y2):

    slope = (y2-y1)/(x2-x1)
    intercept = y1 - slope*x1
    line_length = np.sqrt((y2-y1)**2+(x2-x1)**2)
    return(slope,intercept,line_length)

def to_keep_index(obs, std=1.5):
    return np.array(abs(obs - np.mean(obs)) < std*np.std(obs))

def mean(list):
    mean = 0

    for i in list:
        mean +=i

    mean = mean/len(list)

    return(mean)

def leftLines(slope,intercept):

    if len(leftSlope) > 5 and len(leftIntercept) > 5:
        leftSlope.popleft()
        leftIntercept.popleft()

        leftSlope.append(slope)
        leftIntercept.append(intercept)

    else:
        leftSlope.append(slope)
        leftIntercept.append(intercept)

    slopeAvg     = mean(leftSlope)
    interceptAvg = mean(leftIntercept)

    return(slopeAvg,interceptAvg)

def rightLines(slope,intercept):

    if len(rightSlope) > 5 and len(rightIntercept) > 5:
        rightSlope.popleft()
        rightIntercept.popleft()

        rightSlope.append(slope)
        rightIntercept.append(intercept)
    else:
        rightSlope.append(slope)
        rightIntercept.append(intercept)

    slopeAvg     = mean(rightSlope)
    interceptAvg = mean(rightIntercept)

    return(slopeAvg,interceptAvg)


#Modified code from Cody Nicholson and Jeff Wen
def avg_lines(image,lines):

    neg = np.empty([1,3])
    pos = np.empty([1,3])

    #Calculate slopes for each line to identify the positive and negative lines
    for line in lines:
        for x1,y1,x2,y2 in line:

            slope,intercept,line_length = mathfunc(x1,y1,x2,y2)

            if slope < 0 and line_length > 10:
                neg = np.append(neg,np.array([[slope, intercept, line_length]]),axis = 0)

            elif slope > 0 and line_length > 10:
                pos = np.append(pos,np.array([[slope, intercept, line_length]]),axis = 0)


    #Just keep the observations with slopes with 2 std dev
    neg = neg[to_keep_index(neg[:,0])]
    pos = pos[to_keep_index(pos[:,0])]

    #Weighted average of the slopes and intercepts based on the length of the line segment
    neg_lines = np.dot(neg[1:,2],neg[1:,:2])/np.sum(neg[1:,2]) if len(neg[1:,2]) > 0 else None
    pos_lines = np.dot(pos[1:,2],pos[1:,:2])/np.sum(pos[1:,2]) if len(pos[1:,2]) > 0 else None

    lSlope  = pos_lines[0]
    lIntercept      = pos_lines[1]

    AvgPositiveM, AvgLeftB = leftLines(lSlope,lIntercept)

    rSlope     = neg_lines[0]
    rIntercept = neg_lines[1]

    AvgNegitiveM, AvgRightB = rightLines(rSlope,rIntercept)

    imshape = image.shape
    y_max   = imshape[0]
    y_min   = 300

    x1_Left = (y_max - AvgLeftB)/AvgPositiveM
    y1_Left = y_max
    x2_Left = (y_min - AvgLeftB)/AvgPositiveM
    y2_Left = y_min

    x1_Right = (y_max - AvgRightB)/AvgNegitiveM
    y1_Right = y_max
    x2_Right = (y_min - AvgRightB)/AvgNegitiveM
    y2_Right = y_min

    #Put left and right lane onto original image
    cv2.line(image, (int(x1_Left), int(y1_Left)), (int(x2_Left), int(y2_Left)), [0,200,0], 15) #avg Left Line
    cv2.line(image, (int(x1_Right), int(y1_Right)), (int(x2_Right), int(y2_Right)), [0,200,0], 15) #avg Right Line

    leftLaneSlope  = AvgPositiveM
    rightLaneSlope =  AvgNegitiveM

    return(leftLaneSlope, rightLaneSlope)

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
    cv2.imwrite('1.png', processedImage)
    # For 3rd person vertices = np.array([[200,1000],[150,450],[400,225],[800,225],[850,450],[850,700],], np.int32)
    #From hood of car
    vertices = np.array([[5,590],[5,520],[525,320],[1020,480],[1020,590],], np.int32)
    #vertices = np.array([[433,383],[70,675],[25,650],[455,220],[600,200],[1000,630],[675,675],[615,380],], np.int32)
    #vertices = np.array([[250,425],[450,300],[640,300],[840,425],], np.int32)
    processedImage = cv2.GaussianBlur(processedImage,(5,5),0)
    cv2.imwrite('2.png', processedImage)
    processedImage = roi(processedImage, [vertices])
    cv2.imwrite('3.png', processedImage)

    lines = cv2.HoughLinesP(processedImage, 1, np.pi/180, 180, 20, 15)

    draw_lines(processedImage,lines)
    cv2.imwrite('4.png', processedImage)

    left,right = avg_lines(originalImage, lines)

    return(originalImage,left,right)

def screen_record():

    left  = 0
    right = 0

    last_time = time.time()
    while True:
        #PressKey(W)
        printscreen = grab_screen(region=(0,40,1024,768))
        try:
            new_screen,left,right = image_process(printscreen)
            cv2.imshow('window', new_screen)
            cv2.waitKey(5)
            #cv2.waitKey()
            #cv2.imwrite('processedImage.png', new_screen)
            num_seconds = time.time() - last_time

        except:
            continue
        print(left+right)
        # if left+right > 0.6:
        #      turnLeft()
        # elif left+right<-0.6:
        #      turnRight()
        # else:
        #     goStraight()
        # if num_seconds > 100:
        #       break
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
