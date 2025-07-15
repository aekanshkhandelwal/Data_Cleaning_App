import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Cleaning App", layout="wide")
st.title("🧹 Data Cleaning App")

# Sidebar
st.sidebar.header("Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your file", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    cleaned_data = data.copy()
    updates_summary = []

    st.sidebar.header("Data Cleaning Options")

    # Smart Clean Button
    if st.sidebar.button("🧠 Smart Clean"):
        original_shape = cleaned_data.shape
        # Remove duplicates
        cleaned_data = cleaned_data.drop_duplicates()
        updates_summary.append("✅ Removed duplicate rows.")

        # Convert to lowercase & strip whitespace
        str_cols = cleaned_data.select_dtypes(include='object').columns
        for col in str_cols:
            cleaned_data[col] = cleaned_data[col].str.lower().str.strip()
        updates_summary.append("🔠 Lowercased and trimmed whitespace in string columns.")

        # Drop fully empty rows
        null_rows_before = cleaned_data.shape[0]
        cleaned_data = cleaned_data.dropna(how='all')
        null_rows_after = cleaned_data.shape[0]
        dropped = null_rows_before - null_rows_after
        if dropped > 0:
            updates_summary.append(f"🧺 Dropped {dropped} completely empty rows.")

        updates_summary.append(f"📏 Shape after smart clean: {cleaned_data.shape} (was {original_shape})")

    # Show missing value summary
    if st.sidebar.checkbox("Show Missing Value Summary"):
        st.subheader("🕳️ Missing Value Summary")
        null_counts = cleaned_data.isnull().sum()
        null_counts = null_counts[null_counts > 0]
        if not null_counts.empty:
            st.write("Missing values per column:")
            st.dataframe(null_counts.to_frame(name='Missing Values'))
            st.info(f"🔢 Total missing values: {null_counts.sum()}")
        else:
            st.success("✅ No missing values found.")

    # Highlight Duplicates
    if st.sidebar.checkbox("Highlight Duplicate Rows"):
        duplicate_rows = cleaned_data[cleaned_data.duplicated()]
        if not duplicate_rows.empty:
            st.warning(f"⚠️ Found {len(duplicate_rows)} duplicate rows:")
            st.dataframe(duplicate_rows)
        else:
            st.success("✅ No duplicate rows found.")

    # Remove Duplicates
    if st.sidebar.checkbox("Remove Duplicate Rows"):
        cleaned_data = cleaned_data.drop_duplicates()
        updates_summary.append(f"✅ Duplicates removed. New shape: {cleaned_data.shape}")

    # Convert to lowercase
    if st.sidebar.checkbox("Convert String Columns to Lowercase"):
        str_cols = cleaned_data.select_dtypes(include='object').columns
        for col in str_cols:
            cleaned_data[col] = cleaned_data[col].str.lower()
        updates_summary.append("✅ Converted all string columns to lowercase")

    # Drop rows with missing values
    if st.sidebar.checkbox("Drop Rows with Missing Values"):
        cleaned_data = cleaned_data.dropna()
        updates_summary.append(f"✅ Dropped rows with missing values. New shape: {cleaned_data.shape}")

    # Handle Missing Values
    if st.sidebar.checkbox("Handle Missing Values"):
        st.subheader("🔧 Missing Value Imputation")
        missing_cols = cleaned_data.columns[cleaned_data.isnull().any()].tolist()

        if missing_cols:
            for col in missing_cols:
                col_type = str(cleaned_data[col].dtype)
                st.markdown(f"### `{col}` ({col_type}) — {cleaned_data[col].isnull().sum()} missing values")

                if pd.api.types.is_numeric_dtype(cleaned_data[col]):
                    st.info("💡 Recommended: Mean, Median, or Remove Rows")
                else:
                    st.info("💡 Recommended: Mode, Custom Value, or Remove Rows")

                method = st.selectbox(
                    f"Choose method for `{col}`",
                    ["Mean", "Median", "Mode", "Custom Value", "Remove Rows"],
                    key="method_" + col
                )

                if method == "Mean" and pd.api.types.is_numeric_dtype(cleaned_data[col]):
                    cleaned_data[col].fillna(cleaned_data[col].mean(), inplace=True)
                    updates_summary.append(f"✅ Filled missing in `{col}` with mean")

                elif method == "Median" and pd.api.types.is_numeric_dtype(cleaned_data[col]):
                    cleaned_data[col].fillna(cleaned_data[col].median(), inplace=True)
                    updates_summary.append(f"✅ Filled missing in `{col}` with median")

                elif method == "Mode":
                    mode_val = cleaned_data[col].mode()
                    if not mode_val.empty:
                        cleaned_data[col].fillna(mode_val[0], inplace=True)
                        updates_summary.append(f"✅ Filled missing in `{col}` with mode")

                elif method == "Custom Value":
                    custom_value = st.text_input(f"Enter custom value for `{col}`", key="custom_" + col)
                    if st.button(f"Apply Custom Fill for `{col}`", key="btn_custom_" + col):
                        if custom_value:
                            try:
                                if pd.api.types.is_numeric_dtype(cleaned_data[col]):
                                    cast_value = float(custom_value)
                                else:
                                    cast_value = custom_value
                                cleaned_data[col].fillna(cast_value, inplace=True)
                                updates_summary.append(f"✅ Filled `{col}` with custom value")
                            except ValueError:
                                st.warning(f"⚠️ Invalid type for `{col}`")
                        else:
                            st.warning("⚠️ Please enter a value")

                elif method == "Remove Rows":
                    original_shape = cleaned_data.shape
                    cleaned_data = cleaned_data[cleaned_data[col].notnull()]
                    updates_summary.append(f"🗑️ Removed rows where `{col}` was null. New shape: {cleaned_data.shape}")

        else:
            st.success("✅ No missing values found.")

    # Drop Specific Columns
    if st.sidebar.checkbox("Drop Specific Columns"):
        columns_to_drop = st.multiselect("Select columns to drop", cleaned_data.columns)
        if columns_to_drop:
            cleaned_data.drop(columns=columns_to_drop, inplace=True)
            updates_summary.append(f"🗑️ Dropped columns: {columns_to_drop}")

    # Rename Columns (with Enter button)
    if st.sidebar.checkbox("Rename Columns"):
        st.subheader("✏️ Rename Columns")
        column_to_rename = st.selectbox("Select column", cleaned_data.columns, key="rename_select")
        new_column_name = st.text_input("Enter new name", key="new_name_input")
        if st.button("Rename Column"):
            if new_column_name and new_column_name != column_to_rename:
                if new_column_name in cleaned_data.columns:
                    st.warning("⚠️ That name already exists.")
                else:
                    cleaned_data.rename(columns={column_to_rename: new_column_name}, inplace=True)
                    updates_summary.append(f"🔤 Renamed `{column_to_rename}` → `{new_column_name}`")
            else:
                st.warning("⚠️ Please enter a valid new name.")

    # Show Original vs Cleaned Data
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Original Data")
        st.dataframe(data)
    with col2:
        st.subheader("🧹 Cleaned Data Preview")
        st.dataframe(cleaned_data)

    # Cleaning summary
    if updates_summary:
        st.subheader("📝 Cleaning Summary")
        for update in updates_summary:
            st.write(update)

    # Download cleaned data
    csv = cleaned_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Cleaned Data as CSV", csv, "cleaned_data.csv", "text/csv")

else:
    st.info("📁 Please upload a CSV file to begin.")
