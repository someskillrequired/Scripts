import pandas as pd

def find_diff(start_file, end_file, sheets, output_file):

    with open(output_file, "w") as f_out:  # open once for all sheets
        for sheet in sheets:
            try:
                df1 = pd.read_excel(start_file, sheet_name=sheet, index_col=0)
                df2 = pd.read_excel(end_file, sheet_name=sheet, index_col=0)
            except Exception as e:
                f_out.write(f"Error reading sheet '{sheet}': {e}\n\n")
                continue

            # --- Ensure both have same shape / columns ---
            df2 = df2.reindex_like(df1)

            # --- Compare ---
            output_lines = [f"========= {sheet} Changes =========\n"]
            max_col_len = max(len(str(col)) for col in df1.columns)
            max_val_len = 0

            # Find max value length for alignment
            for row_label in df1.index:
                for col_label in df1.columns:
                    v1 = df1.at[row_label, col_label]
                    v2 = df2.at[row_label, col_label]
                    if pd.isna(v1):
                        v1 = None
                    if pd.isna(v2):
                        v2 = None
                    if v1 != v2:
                        max_val_len = max(max_val_len, len(str(v1)))

            # Build output for this sheet
            for row_label in df1.index:
                diffs = []
                for col_label in df1.columns:
                    v1 = df1.at[row_label, col_label]
                    v2 = df2.at[row_label, col_label]
                    if pd.isna(v1):
                        v1 = None
                    if pd.isna(v2):
                        v2 = None
                    if v1 != v2:
                        diffs.append(
                            f"\t{str(col_label).ljust(max_col_len-10)} {str(v1).rjust(max_val_len)} -> {v2}"
                        )
                if diffs:
                    output_lines.append(f"{row_label}")
                    output_lines.extend(diffs)
                    output_lines.append("")  # Blank line

            if len(output_lines) == 1:
                output_lines.append("No differences found.\n")

            # Write this sheet's results to file
            f_out.write("\n".join(output_lines))
            f_out.write("\n\n")

    print(f"Comparison complete. Differences written to {output_file}")

if __name__ == "__main__":
    # --- Configuration ---
    file1 = "ZXRulesModv1.xlsx"
    file2 = "ZXRulesModv2.xlsx"
    output_file = "diff_output.txt"

    sheets = ["Campaigns", "Commands", "Entities", "Global", "MapConditions", "MapThemes", "Mayors"]
    find_diff(file1, file2, sheets, output_file)
