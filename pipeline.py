import sys
from PIL import Image
import pytesseract

from parser import parse_ocr_text
from matcher import load_master_list, match_row
from exporter import export_to_excel
from preprocess import preprocess_image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def run_ocr(image_path):
    img = preprocess_image(image_path)
    new_size = (img.width * 3, img.height * 3)
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    text = pytesseract.image_to_string(img, config="--psm 6")
    return text


def process_catalog_image(image_path, master_list_path="master_list/master_list.csv"):
    raw_text = run_ocr(image_path)
    print("--- RAW OCR TEXT ---")
    print(raw_text)
    print("--- END RAW ---")
    parsed_rows = parse_ocr_text(raw_text)
    master_df = load_master_list(master_list_path)
    results = [match_row(row, master_df) for row in parsed_rows]
    return results


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else "test_clean.png"
    results = process_catalog_image(image_path)

    print(f"\nProcessed: {image_path}\n" + "=" * 50)
    for r in results:
        print(f"OCR read:  {r['sku']} | {r['name']} | {r['price']} | qty:{r['qty']}")
        print(f"Matched:   {r['matched_sku']} | {r['matched_name']} (score: {r['match_score']})")
        print(f"Status:    {r['status']}")
        print("-" * 50)
    export_to_excel(results)