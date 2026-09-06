import pandas as pd
from rapidfuzz import process, fuzz
from parser import parse_ocr_text

def load_master_list(path="master_list/master_list.csv"):
    return pd.read_csv(path)

def match_row(parsed_row, master_df, threshold=85):
    if not parsed_row["name"]:
        return {**parsed_row, "matched_sku": None, "matched_name": None,
                "match_score": 0, "status": "REJECTED - no name extracted"}

    choices = master_df["name"].tolist()
    result = process.extractOne(parsed_row["name"], choices, scorer=fuzz.ratio)

    if result is None:
        return {**parsed_row, "matched_sku": None, "matched_name": None,
                "match_score": 0, "status": "REJECTED - no match found"}

    match_name, score, idx = result
    master_row = master_df.iloc[idx]

    if score >= threshold:
        status = "ACCEPTED"
    elif score >= 60:
        status = "FLAGGED - needs review"
    else:
        status = "REJECTED - low confidence"

    return {**parsed_row, "matched_sku": master_row["sku"], "matched_name": master_row["name"],
            "match_score": round(score, 1), "status": status}

def run_matching(raw_ocr_text, master_list_path="master_list/master_list.csv"):
    master_df = load_master_list(master_list_path)
    parsed_rows = parse_ocr_text(raw_ocr_text)
    return [match_row(row, master_df) for row in parsed_rows]

if __name__ == "__main__":
    sample_ocr_output = """SKU-1001 Widget-42 $12.50 qty:100
SKU-1062 Bracket-Steel $4.75 qty: 259)"""

    results = run_matching(sample_ocr_output)
    for r in results:
        print(f"OCR read: {r['sku']} / {r['name']} / {r['price']} / qty:{r['qty']}")
        print(f"  -> Matched to: {r['matched_sku']} / {r['matched_name']} (score: {r['match_score']})")
        print(f"  -> Status: {r['status']}")
        print()