from PIL import Image
import os
import cv2
import skimage.filters as filters
import numpy as np

if __name__ == '__main__':
    # im = Image.open('gray_test.jpg')
    # (x, y) = im.size  # 读取图片尺寸（像素）
    # x_1 = int(x / 2)  # 定义缩小后的标准宽度
    # y_1 = int(y * x_1 / x)  # 计算缩小后的高度
    # out = im.resize((x_1, y_1), Image.ANTIALIAS)  # 改变尺寸，保持图片高品质
    # #判断图片的通道模式，若图片在RGBA模式下，需先将其转变为RGB模式
    # if out.mode=='RGBA':
    #     #转化为rgb格式
    #     out=out.convert('RGB')
    #    #最后保存为jpg格式的图片，这里因为图片本身为jpg所以后缀不更改
    # out.save('pictures_new.jpg')

    img = cv2.imread("improve_test2.jpg", -1)
    org = cv2.imread("gray_test.jpg", -1)
    i_height, i_width = img.shape[:2]
    o_height, o_width = org.shape[:2]

    # 放大图像
    fx = o_width / i_width
    fy = o_height / i_height
    enlarge = cv2.resize(img, (0, 0), fx=fx, fy=fy, interpolation=cv2.INTER_AREA)
    # enlarge = cv2.resize(enlarge, (0, 0), fx=1, fy=1, interpolation=cv2.INTER_LANCZOS4)
    # enlarge = cv2.resize(enlarge, (0, 0), fx=1, fy=1, interpolation=cv2.INTER_NEAREST)
    clahe = cv2.createCLAHE(clipLimit=1, tileGridSize=(5, 5))  # 对图像进行分割，10*10
    img4 = clahe.apply(enlarge)  # 进行直方图均衡化
    smooth = cv2.GaussianBlur(img4, (33, 33), 0)
    #
    #
    # # divide gray by morphology image
    division = cv2.divide(img4, smooth, scale=255)

    sharp = filters.unsharp_mask(division, radius=1.5, amount=2.5, preserve_range=False)
    sharp = (255 * sharp).clip(0, 255).astype(np.uint8)


    # # 显示
    cv2.imshow("org", org)
    # cv2.imshow("compass", img)
    cv2.imshow("enlarge", img4)
    cv2.imshow("sharp", sharp)
    cv2.waitKey(0)