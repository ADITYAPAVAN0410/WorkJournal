import streamlit as st
import Workjournal
import pandas as pd

st.set_page_config(page_title="WorkJournal", layout="wide")
st.title("💻 WorkJournal")

# 1. LOGGING SECTION
with st.expander("➕ Log New Activity"):
    with st.form("log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        description = col1.text_input("Activity Description")
        category = col2.selectbox("Category", Workjournal.VALID_CATEGORIES)
        if st.form_submit_button("Log Task"):
            Workjournal.log_task(description, category)
            st.rerun()

# 2. DATA DISPLAY
st.header("📋 Activity Log")
entries = Workjournal.load_journal()

if entries:
    display_data = []
    last_date = None
    
    # Track which real entries (not separators) have which original index
    # This helps map serial number to the actual data row
    for idx, e in enumerate(entries, 1):
        current_date = Workjournal.fmt_date(e["timestamp"])
        
        # Day Boundary Logic
        if last_date and current_date != last_date:
            display_data.append({
                "S.No": "---", 
                "Date": "---", 
                "Local Time": "---", 
                "Category": "---", 
                "Activity": f"--- End of {last_date} / Start of {current_date} ---"
            })
        
        display_data.append({
            "S.No": idx,
            "Date": current_date,
            "Local Time": Workjournal.fmt_time(e["timestamp"]),
            "Category": e["category"].capitalize(),
            "Activity": e["activity_description"]
        })
        last_date = current_date
    
    df = pd.DataFrame(display_data)
    st.table(df)

    # 3. PRINT / EXPORT SECTION
    if st.button("🖨️ Print Report"):
        st.session_state.show_modal = True

    if st.session_state.get("show_modal"):
        with st.container():
            st.subheader("Select Range for Report")
            # Only allow selecting real entries (not separators)
            real_indices = [idx for idx, row in enumerate(display_data) if row["S.No"] != "---"]
            
            if real_indices:
                col_a, col_b = st.columns(2)
                start_idx = col_a.number_input("From Serial", 1, len(real_indices), 1)
                end_idx = col_b.number_input("To Serial", start_idx, len(real_indices), len(real_indices))
                
                if st.button("Generate Downloadable HTML"):
                    # Extract the range of interest from the original display_data
                    # Because we added separators, we need to find the correct slice 
                    # that includes the separators if they fall between the selected serials.
                    
                    # Logic: Identify the rows in display_data that correspond to serial numbers [start_idx, end_idx]
                    # and include any separators between them.
                    
                    filtered_data = []
                    # Find the position in display_data for start_idx and end_idx
                    # This is simplified by filtering by the S.No column
                    
                    # Filter df: 
                    # 1. Convert S.No to numeric, handle '---' as NaN
                    df_numeric = df.copy()
                    df_numeric['S.No'] = pd.to_numeric(df['S.No'], errors='coerce')
                    
                    # 2. Slice based on the numeric serial numbers
                    # We need to find the rows from the first appearance of start_idx 
                    # to the last appearance of end_idx
                    start_row = df_numeric[df_numeric['S.No'] == start_idx].index[0]
                    end_row = df_numeric[df_numeric['S.No'] == end_idx].index[0]
                    
                    report_df = df.iloc[start_row:end_row+1]
                    
                    html_content = f"""
                    <html>
                    <head><style>
                        table {{ border-collapse: collapse; width: 100%; }} 
                        th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                        h2 {{ font-family: sans-serif; }}
                    </style></head>
                    <body>
                        <h2>Status Report (Serial {start_idx} to {end_idx})</h2>
                        {report_df.to_html(index=False)}
                    </body>
                    </html>
                    """
                    st.download_button(
                        label="⬇️ Download Range Report",
                        data=html_content,
                        file_name=f"Report_{start_idx}_to_{end_idx}.html",
                        mime="text/html"
                    )
else:
    st.info("No logs yet.")
