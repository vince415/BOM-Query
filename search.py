import streamlit as st
import pandas as pd
import io

# Page Configuration
st.set_page_config(page_title="SKU Global Search", layout="wide")

st.title("📊 BOM Query Where-Use Navigator")

# --- 1. File Upload Section ---
uploaded_file = st.file_uploader("Step 1: Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        @st.cache_data
        def load_data(file):
            # Load the specific worksheet
            return pd.read_excel(file, sheet_name='Current SKU')


        df = load_data(uploaded_file)

        # --- 2. Global Search Interface ---
        # Using a form to prevent automatic refreshing while typing
        with st.form("search_form"):
            st.write("🔍 Step 2: Global Search (Search across all columns)")

            # Single input box for any information (SKU, Code, Name, etc.)
            global_search_term = st.text_input(
                "Enter your search term (Case-Insensitive):",
                placeholder="Type any code or info here...",
                key="global_search"
            )

            st.markdown("---")
            _, btn_col, _ = st.columns([2, 1, 2])
            with btn_col:
                search_submitted = st.form_submit_button("🚀 Run Search", use_container_width=True, type="primary")

        # --- 3. Global Search Logic ---
        if search_submitted:
            if global_search_term:
                # Logic:
                # 1. Convert the entire dataframe to string
                # 2. Convert to lowercase
                # 3. Check if any cell in a row equals the search term (case-insensitive)

                search_val = str(global_search_term).lower().strip()

                # We use .applymap to normalize the data for comparison
                # Then check if any column in the row meets the condition
                mask = df.astype(str).apply(lambda x: x.str.lower() == search_val).any(axis=1)
                filtered_df = df[mask]

                st.subheader(f"✅ Search Results ({len(filtered_df)} rows found)")
            else:
                # If search button is clicked with empty input, show all data
                filtered_df = df.copy()
                st.subheader("📋 Showing All Data (Empty Search)")

            st.dataframe(filtered_df, use_container_width=True)

            # --- 4. Export to Excel Feature ---
            if not filtered_df.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='Filtered_Results')

                excel_data = output.getvalue()
                st.download_button(
                    label="📥 Export These Results to Excel (.xlsx)",
                    data=excel_data,
                    file_name="global_search_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            # Initial state: Show a preview
            st.info("💡 Enter any code in the box above and click 'Run Search'.")
            st.subheader("📋 Data Preview (First 15 rows)")
            st.dataframe(df.head(15), use_container_width=True)

    except Exception as e:
        st.error("❌ Error: Could not find a worksheet named 'Current SKU'.")
        st.info(f"Details: {e}")
else:
    st.warning("👋 Welcome! Please upload an Excel file to begin.")