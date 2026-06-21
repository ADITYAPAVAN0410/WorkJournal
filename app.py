import io
import streamlit as st
import Workjournal
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

    for idx, e in enumerate(entries, 1):
        current_date = Workjournal.fmt_date(e["timestamp"])

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

    # 3. EXPORT SECTION
    if st.button("🖨️ Print / Export Report"):
        st.session_state.show_modal = True

    if st.session_state.get("show_modal"):
        with st.container():
            st.subheader("Select Range for Report")
            real_indices = [idx for idx, row in enumerate(display_data) if row["S.No"] != "---"]

            if real_indices:
                col_a, col_b = st.columns(2)
                start_idx = col_a.number_input("From Serial", 1, len(real_indices), 1)
                end_idx = col_b.number_input("To Serial", start_idx, len(real_indices), len(real_indices))

                # --- shared slice logic ---
                df_numeric = df.copy()
                df_numeric["S.No"] = pd.to_numeric(df["S.No"], errors="coerce")
                start_row = df_numeric[df_numeric["S.No"] == start_idx].index[0]
                end_row = df_numeric[df_numeric["S.No"] == end_idx].index[0]
                report_df = df.iloc[start_row : end_row + 1]

                col_h, col_p, col_x = st.columns(3)

                # --- HTML download ---
                with col_h:
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
                        label="⬇️ Download HTML",
                        data=html_content,
                        file_name=f"Report_{start_idx}_to_{end_idx}.html",
                        mime="text/html"
                    )

                # --- PDF download ---
                with col_p:
                    def build_pdf(dataframe, title):
                        buf = io.BytesIO()
                        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=40, bottomMargin=40)
                        styles = getSampleStyleSheet()
                        elems = [Paragraph(title, styles["Title"]), Spacer(1, 12)]

                        headers = list(dataframe.columns)
                        rows = [headers] + dataframe.values.tolist()
                        # Convert every cell to string
                        rows = [[str(c) for c in row] for row in rows]

                        tbl = Table(rows, repeatRows=1)
                        tbl.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
                            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE",   (0, 0), (-1, -1), 8),
                            ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#DEEAF1")]),
                            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
                            ("WORDWRAP",   (0, 0), (-1, -1), "WORD"),
                        ]))
                        elems.append(tbl)
                        doc.build(elems)
                        buf.seek(0)
                        return buf.read()

                    pdf_bytes = build_pdf(report_df, f"Status Report  (Serial {start_idx} – {end_idx})")
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"Report_{start_idx}_to_{end_idx}.pdf",
                        mime="application/pdf"
                    )

                # --- Excel download (one sheet per day) ---
                with col_x:
                    def build_excel(dataframe):
                        buf = io.BytesIO()
                        # Only real rows (skip separator rows)
                        real_df = dataframe[dataframe["S.No"] != "---"].copy()

                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            # All-entries sheet
                            real_df.to_excel(writer, sheet_name="All Entries", index=False)
                            ws_all = writer.sheets["All Entries"]
                            for col in ws_all.columns:
                                ws_all.column_dimensions[col[0].column_letter].width = max(
                                    len(str(col[0].value or "")),
                                    *(len(str(c.value or "")) for c in col[1:]),
                                ) + 4

                            # One sheet per day
                            for date_val, group in real_df.groupby("Date", sort=False):
                                sheet_name = str(date_val)[:31]  # Excel sheet name max 31 chars
                                group.to_excel(writer, sheet_name=sheet_name, index=False)
                                ws = writer.sheets[sheet_name]
                                for col in ws.columns:
                                    ws.column_dimensions[col[0].column_letter].width = max(
                                        len(str(col[0].value or "")),
                                        *(len(str(c.value or "")) for c in col[1:]),
                                    ) + 4

                        buf.seek(0)
                        return buf.read()

                    excel_bytes = build_excel(report_df)
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=excel_bytes,
                        file_name=f"Report_{start_idx}_to_{end_idx}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

else:
    st.info("No logs yet.")
