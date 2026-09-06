from logging import config

import pytesseract
from PIL import Image
import sys

# Tell pytesseract where Tesseract is installed on Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_path):
    img = Image.open(image_path)
    new_size = (img.width*3, img.height*3)
    resize = img.resize(new_size, Image.Resampling.LANCZOS)
    img = img.convert("L")
    img = img.point(lambda pixel:0 if pixel <150 else 255)
    text = pytesseract.image_to_string(img)
    return text


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "test_clean.png"
    raw_text = extract_text(path)
    print("--- RAW OCR OUTPUT ---")
    print(raw_text)
    print("--- END ---")