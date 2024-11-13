import cv2
import numpy as np


def increase_contrast(image):
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    yuv_image[:, :, 0] = cv2.equalizeHist(yuv_image[:, :, 0])
    output_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)
    return output_image


def decrease_brightness(image, alpha):
    darker_image = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
    return darker_image


image = cv2.imread('image_path')
result_img = increase_contrast(decrease_brightness(image, 0.8))

cv2.imwrite('edited.jpg', result_img)
