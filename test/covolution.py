import pprint

import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_matrix(m, color, cmap, title=None):
    rows, cols = len(m), len(m[0])
    fig, ax = plt.subplots(figsize=(cols, rows))
    ax.set_yticks(list(range(rows)))
    ax.set_xticks(list(range(cols)))
    ax.xaxis.tick_top()
    if title is not None:
        ax.set_title('{} {}'.format(title, m.shape), y=-0.5 / rows)
    plt.imshow(m, cmap=cmap, vmin=0, vmax=1)
    for r in range(rows):
        for c in range(cols):
            text = '{:>3}'.format(int(m[r][c]))
            ax.text(c - 0.2, r + 0.15, text, color=color, fontsize=15)
    plt.show()


def show_inputs(m, title='Inputs'):
    show_matrix(m, 'b', plt.cm.Vega10, title)


def show_kernel(m, title='Kernel'):
    show_matrix(m, 'r', plt.cm.RdBu_r, title)


def show_output(m, title='Output'):
    show_matrix(m, 'g', plt.cm.GnBu, title)

def processImage(image):
  image = cv2.imread(image)
  image = cv2.cvtColor(src=image, code=cv2.COLOR_BGR2GRAY)
  return image


def convolve2D(image, kernel, padding=0, strides=1):
    # Cross Correlation
    kernel = np.flipud(np.fliplr(kernel))

    # Gather Shapes of Kernel + Image + Padding
    xKernShape = kernel.shape[0]
    yKernShape = kernel.shape[1]
    xImgShape = image.shape[0]
    yImgShape = image.shape[1]

    # Shape of Output Convolution
    xOutput = int(((xImgShape - xKernShape + 2 * padding) / strides) + 1)
    yOutput = int(((yImgShape - yKernShape + 2 * padding) / strides) + 1)
    output = np.zeros((xOutput, yOutput))

    # Apply Equal Padding to All Sides
    if padding != 0:
        imagePadded = np.zeros((image.shape[0] + padding*2, image.shape[1] + padding*2))
        imagePadded[int(padding):int(-1 * padding), int(padding):int(-1 * padding)] = image
        print(imagePadded)
    else:
        imagePadded = image

    # Iterate through image
    for y in range(image.shape[1]):
        # Exit Convolution
        if y > image.shape[1] - yKernShape:
            break
        # Only Convolve if y has gone down by the specified Strides
        if y % strides == 0:
            for x in range(image.shape[0]):
                # Go to next row once kernel is out of bounds
                if x > image.shape[0] - xKernShape:
                    break
                try:
                    # Only Convolve if x has moved by the specified Strides
                    if x % strides == 0:
                        output[x, y] = (kernel * imagePadded[x: x + xKernShape, y: y + yKernShape]).sum()
                except:
                    break

    return output


def convolution_matrix(image, kernel, padding=0, strides=10):
    m_rows, m_cols = len(image), len(image[0])  # matrix rows, cols
    k_rows, k_cols = len(kernel), len(kernel[0])  # kernel rows, cols

    # Shape of Output Convolution
    rows = int(((m_rows - k_rows + 2 * padding) / strides) + 1)
    cols = int(((m_rows - k_rows + 2 * padding) / strides) + 1)

    # convolution matrix
    v = np.zeros((rows * cols, m_rows, m_cols))

    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            v[i][r:r + k_rows, c:c + k_cols] = kernel

    v = v.reshape((rows * cols), -1)
    return v, rows, cols

def column_vector(m):
    return m.flatten().reshape(-1, 1)

if __name__ == '__main__':
    # Grayscale Image
    image = processImage('gray_test.jpg')
    image = image[:200,:200]
    print(image.shape)
    kernel_size = 3

    # Edge Detection Kernel
    # kernel = np.random.randint(1,10, size=(kernel_size, kernel_size))
    # kernel = np.array([
    #     [-1, -1, -1, -1],
    #     [-1, 8, -1, -6],
    #     [-1, -1, -1, 2],
    #     [-1, -1, -1, 2],
    # ])
    kernel = np.array([
        [1, 2, 4],
        [1, 1, 3],
        [1, 2, 4]
    ])
    C, rows, cols = convolution_matrix(image, kernel)
    # show_kernel(C, 'Convolution Matrix')
    x = column_vector(image)
    print(C.shape[0], C.shape[1])
    compressed = np.dot(C, x)
    compressed_output = compressed.reshape(rows, cols)

    origin = np.dot(C.T, compressed)
    origin_output = origin.reshape(image.shape[0], image.shape[1])
    norm_image = cv2.normalize(origin_output, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    norm_output = norm_image.astype(np.uint8)
    print(norm_output)

    cv2.imshow("org", image)
    # cv2.imshow("compass", img)
    cv2.imshow("sharp", norm_output)
    cv2.waitKey(0)



    # try:
    #     m = np.dot(C.T, C)
    #     print(m)
    #     print(np.linalg.det(m))
    #     inverse = np.linalg.inv(m)
    # except np.linalg.LinAlgError as e:
    #     # Not invertible. Skip this one.
    #     print(e)
    # else:
    #     origin = np.dot(inverse ,C.T) * compressed
    #     print(origin.shape)
    #     output2 = origin.reshape(image.shape[0], image.shape[1])
    #     pprint.pprint(output2)

    # Convolve and Save Output
    # output = convolve2D(image, kernel)
    # pprint.pprint(output.shape)
    # cv2.imwrite('2DConvolved.jpg', output)