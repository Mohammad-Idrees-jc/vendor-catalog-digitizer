import pandas as pd

def export_to_excel(results, output_path="output/catalog_output.xlsx"):
    """Split results by status and write each group to its own Excel sheet."""
    df = pd.DataFrame(results)

    accepted = df[df["status"] == "ACCEPTED"]
    flagged = df[df["status"] == "FLAGGED - needs review"]
    rejected = df[df["status"].str.startswith("REJECTED")]

    # Only keep the columns a client actually needs to see
    display_cols = ["matched_sku", "matched_name", "price", "qty", "match_score", "status"]

    # Combined sheet: everything worth importing, flagged rows included,
    # so the user can eyeball and delete bad rows manually before using it
    import_ready = pd.concat([flagged, accepted])[display_cols]

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        import_ready.to_excel(writer, sheet_name="Import Ready", index=False)
        accepted[display_cols].to_excel(writer, sheet_name="Accepted Only", index=False)
        flagged[display_cols].to_excel(writer, sheet_name="Needs Review", index=False)
        rejected[display_cols].to_excel(writer, sheet_name="Rejected", index=False)

    print(f"Saved: {output_path}")
    print(f"  Accepted: {len(accepted)}")
    print(f"  Needs review: {len(flagged)}")
    print(f"  Rejected: {len(rejected)}")