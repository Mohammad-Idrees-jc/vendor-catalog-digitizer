import streamlit as st
import pandas as pd
import os
import tempfile

from pipeline import process_catalog_image
from exporter import export_to_excel
from matcher import load_master_list

MASTER_LIST_PATH = "master_list/master_list.csv"

st.set_page_config(page_title="Vendor Catalog Digitizer", layout="wide")
st.title("Vendor Catalog Digitizer")

tab1, tab2 = st.tabs(["Digitize Catalog", "Manage Product List"])

# ----------------------------------------------------------------------
# TAB 1: Upload an image, get back matched/flagged Excel results
# ----------------------------------------------------------------------
with tab1:
    st.write("Upload a photo or screenshot of a vendor price list — get back a clean, "
             "structured Excel file with prices and stock quantities matched against "
             "your product database.")

    uploaded_file = st.file_uploader(
        "Upload a catalog image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded catalog", width=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        with st.spinner("Reading image, matching products..."):
            try:
                results = process_catalog_image(tmp_path)
            except Exception as e:
                st.error(f"Something went wrong processing this image: {e}")
                results = []
            finally:
                os.remove(tmp_path)

        if results:
            df = pd.DataFrame(results)

            accepted = df[df["status"] == "ACCEPTED"]
            flagged = df[df["status"] == "FLAGGED - needs review"]
            rejected = df[df["status"].str.startswith("REJECTED")]

            col1, col2, col3 = st.columns(3)
            col1.metric("Accepted", len(accepted))
            col2.metric("Needs Review", len(flagged))
            col3.metric("Rejected", len(rejected))

            display_cols = ["matched_sku", "matched_name", "price", "qty", "match_score", "status"]

            st.subheader("Accepted")
            st.dataframe(accepted[display_cols], width="stretch")

            if len(flagged) > 0:
                st.subheader("Needs Review")
                st.dataframe(flagged[display_cols], width="stretch")

            if len(rejected) > 0:
                st.subheader("Rejected")
                st.dataframe(rejected[display_cols], width="stretch")

            output_path = "temp_output.xlsx"
            export_to_excel(results, output_path)
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Excel file",
                    data=f,
                    file_name="catalog_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            os.remove(output_path)
        else:
            st.warning("No products were detected in this image.")

# ----------------------------------------------------------------------
# TAB 2: View and add products to the master list — no code editing needed
# ----------------------------------------------------------------------
with tab2:
    st.write("This is the reference product database the system matches scanned "
              "catalogs against. Add a new product here whenever a supplier introduces "
              "one that doesn't exist in your system yet.")

    master_df = load_master_list(MASTER_LIST_PATH)
    st.subheader("Current Product List")
    st.dataframe(master_df, width="stretch")

    st.subheader("Add a New Product")
    with st.form("add_product_form", clear_on_submit=True):
        new_sku = st.text_input("SKU (e.g. SKU-3001)")
        new_name = st.text_input("Product Name (e.g. Copper-Fitting-Small)")
        new_price = st.number_input("Reference Price", min_value=0.0, step=0.01)
        new_qty = st.number_input("Reference Quantity", min_value=0, step=1)
        submitted = st.form_submit_button("Add Product")

        if submitted:
            if not new_sku or not new_name:
                st.error("SKU and Product Name are required.")
            elif new_sku in master_df["sku"].values:
                st.error(f"SKU '{new_sku}' already exists in the product list.")
            else:
                new_row = pd.DataFrame([{
                    "sku": new_sku,
                    "name": new_name,
                    "last_known_price": new_price,
                    "last_known_qty": new_qty,
                }])
                updated_df = pd.concat([master_df, new_row], ignore_index=True)
                updated_df.to_csv(MASTER_LIST_PATH, index=False)
                st.success(f"Added '{new_name}' ({new_sku}) to the product list.")
                st.rerun()