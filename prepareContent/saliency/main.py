import cv2
import numpy as np
import random

from . import segmentImage
from . import SaliencyRC

def test_segmentation():
    img3f = cv2.imread("test.jpg")
    img3f = img3f.astype(np.float32)
    img3f *= 1. / 255
    imgLab3f = cv2.cvtColor(img3f,cv2.COLOR_BGR2Lab)
    num,imgInd = segmentImage.SegmentImage(imgLab3f,None,0.5,200,50)

    print(num)
    print(imgInd)
    colors = [[random.randint(0,255),random.randint(0,255),random.randint(0,255)] for _ in range(num)]
    showImg = np.zeros(img3f.shape,dtype=np.int8)
    height = imgInd.shape[0]
    width = imgInd.shape[1]
    for y in range(height):
        for x in range(width):
            if imgInd[y,x].all() > 0:
                showImg[y,x] = colors[imgInd[y,x] % num]
    cv2.imshow("sb",showImg)
    cv2.waitKey(0)

def getSaliency(img, scale=1, segK=10, segMinSize=50):
    start = cv2.getTickCount()

    img3f = img
    img3f *= 1./255
    scaledImg = cv2.resize(img3f, (0,0), fx=1./scale, fy=1./scale)
    sal = SaliencyRC.GetRC(scaledImg , segK, segMinSize)

    #normalize
    min = np.min(sal)
    sal = (sal - min)/(np.max(sal) - min)

    #scale back up
    sal = np.repeat(np.repeat(sal, scale, axis=0), scale, axis=1)

    mask = sal > 0.1
    #mask = np.ma.masked_where(sal > 0.1, sal)

    end = cv2.getTickCount()
    print("Saliency generated in:", (end - start)/cv2.getTickFrequency(), "seconds")

    return mask

def test_rc_map():

    scale = 8

    #img = cv2.imread("test.jpg")
    for y in ["boy.jpg", "brad.jpg", "ca.jpg", "dog.jpg", "lapinozz.jpg", "love.jpg", "man.jpg", "panda.jpg", "ship.jpg"]:
        img = cv2.imread("./content/" + y)[...,::-1]
        mask = getSaliency(img.astype(np.float32), scale)

        maskImg = mask.astype(np.uint8) * 255

        cv2.imshow('mask', np.dstack([maskImg, maskImg, maskImg]))
        cv2.imshow('image', (img))
        cv2.imshow('mask * image', (mask.transpose() * img.transpose()).transpose())

        cv2.waitKey(0)


if __name__ == "__main__":
    #np.set_printoptions(threshold=np.nan)
    #test_segmentation()
    test_rc_map()