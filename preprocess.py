import cv2
import numpy as np
from PIL import Image

def deskew(cv_img):
    """Detect and correct rotation angle of the text in the image."""
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return cv_img

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = cv_img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(cv_img, matrix, (w, h),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    return rotated

def denoise(cv_img):
    """Remove speckle noise while keeping text edges sharp."""
    return cv2.fastNlMeansDenoisingColored(cv_img, None, 10, 10, 7, 21)

def preprocess_image(image_path):
    """Full preprocessing: load -> denoise -> deskew -> return as PIL Image."""
    cv_img = cv2.imread(image_path)
    cv_img = denoise(cv_img)
    cv_img = deskew(cv_img)

    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)