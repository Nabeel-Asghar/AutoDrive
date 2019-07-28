import numpy as np
import time
from PIL import ImageGrab
import cv2
from IPython.display import Image
import pyautogui
from directkeys import PressKey, W, A, S, D



def image_process(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grayEdged =  cv2.Canny(gray, threshold1 = 200, threshold2=300)
    return(grayEdged)


def screen_record():

    last_time = time.time()
    while True:
        PressKey(W)
        printscreen =  np.array(ImageGrab.grab(bbox=(0,40,1024,768)))
        new_screen = image_process(printscreen)
        cv2.imwrite('messigray.png', new_screen)
        num_seconds = time.time() - last_time
        print(num_seconds)
        if num_seconds > 5:
            break
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     cv2.destroyAllWindows()
        #     break

def main():
    for i in range(5,0,-1):
        print(i)
        time.sleep(1)

    screen_record()

if __name__ == "__main__":
    main()
