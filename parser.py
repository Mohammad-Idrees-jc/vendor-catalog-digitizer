import re

def parse_line(line):
    """Extract SKU, product name, price, and qty from one OCR text line."""
    sku_match = re.search(r'SKU-?\S+', line)
    price_match = re.search(r'\$[\d,]+\.\d{2}', line)
    qty_match = re.search(r'qty:?\s*(\d+)', line, re.IGNORECASE)

    sku = sku_match.group() if sku_match else None
    price = price_match.group() if price_match else None
    qty = qty_match.group(1) if qty_match else None

    name = None
    if price_match:
        # Start right after the SKU if one was found, otherwise from the start of the line
        start = sku_match.end() if sku_match else 0
        end = price_match.start()
        name = line[start:end]
        # OCR often adds stray pipe/semicolon/colon characters — strip those out
        name = re.sub(r'[|;:]', '', name).strip()

    return {
        "sku": sku,
        "name": name,
        "price": price,
        "qty": qty,
        "raw_line": line,
    }

def parse_ocr_text(raw_text):
    rows = []
    for line in raw_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(parse_line(line))
    return rows