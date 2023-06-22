import os
import sys
import cv2
import base64
import io
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # file = open('test_byte.jpg', 'rb').read()
    #
    # # We must encode the file to get base64 string
    # file = base64.b64encode(file)
    # print(sys.getsizeof((file)))
    # import cv2

    with open('gray_test.jpg', 'rb') as file:
        binaryData = file.read()
    stru = str(binaryData)
    print(sys.getsizeof((stru)))
    #
    # with open('yes.txt','w') as file:
    #     file.write(output)

    # read the image file
    # img = cv2.imread('test_byte.jpg', 2)
    #
    # ret, bw_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    #
    # # converting to its binary form
    # bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    #
    # cv2.imshow("Binary", bw_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # improve_quality



    # Load the image
    # image = cv2.imread('improve_test.jpg')
    # gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #
    # gray_img_eqhist = cv2.equalizeHist(gray_img)
    #
    # # Create the sharpening kernel
    # # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    # #
    # # # Sharpen the image
    # # sharpened_image = cv2.filter2D(image, -1, kernel)
    #
    # # Save the image
    # cv2.imwrite('gray.jpg', gray_img_eqhist)

    # img = cv2.imread('improve_test.jpg')
    #
    # ## apply image denoising
    #
    # dst = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    # cv2.imwrite('noise.jpg', dst)

    # improvement

    # 读取图像信息
    # img0 = cv2.imread('improve_test.jpg')
    # img1 = cv2.resize(img0, dsize=None, fx=2, fy=2)
    # h, w = img1.shape[:2]
    # print(h, w)
    #
    # img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

    # cv2.namedWindow("W0")
    # cv2.imshow("W0", img1)
    # cv2.waitKey(delay=0)

    # hist0 = cv2.calcHist([img2], [0], None, [256], [0, 255])
    # plt.plot(hist0, label="gray", linestyle="--", color='g')
    # plt.legend()  # 增加图例
    # plt.show()

    # img3 = cv2.equalizeHist(img2)
    # cv2.namedWindow("W1")
    # cv2.imshow("W1", img3)
    # cv2.waitKey(delay=0)

    # hist0 = cv2.calcHist([img2], [0], None, [256], [0, 255])
    # hist1 = cv2.calcHist([img3], [0], None, [256], [0, 255])
    # plt.subplot(2, 1, 1)
    # plt.plot(hist0, label="gray", linestyle="--", color='g')
    # plt.legend()
    # plt.subplot(2, 1, 2)
    # plt.plot(hist1, label="after", linestyle="--", color='r')
    # plt.legend()
    # plt.show()

    # clahe = cv2.createCLAHE(clipLimit=1, tileGridSize=(1, 1))  # 对图像进行分割，10*10
    # img4 = clahe.apply(img2)  # 进行直方图均衡化
    # cv2.namedWindow("W2")
    # cv2.imshow("W2", img4)
    # cv2.waitKey(delay=0)

    # hist0 = cv2.calcHist([img2], [0], None, [256], [0, 255])
    # hist1 = cv2.calcHist([img4], [0], None, [256], [0, 255])
    # plt.subplot(2, 1, 1)
    # plt.plot(hist0, label="gray", linestyle="--", color='g')
    # plt.legend()
    # plt.subplot(2, 1, 2)
    # plt.plot(hist1, label="after", linestyle="--", color='r')
    # plt.legend()
    # plt.show()

