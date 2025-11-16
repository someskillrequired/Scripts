import pandas as pd

#zx_rules = r"C:\project_files\Scripts\unzipped\ZXRules.xlsx"
zx_rules_headers = ["Campaigns", "Commands", "Entities", "Global", "MapConditions", "MapThemes", "Mayors"]
zx_campaign_headers =["BonusItems","HeroPerks","LevelEvents","Missions","Researchs","ResearchTree","Videos"]

def generate_spreadhsheets(zx_rules,ws,file_type):
    results = {m: [] for m in zx_rules_headers}

    # --- Step 1: Group lines under each section ---
    current = None
    with open(zx_rules, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            found = next((m for m in zx_rules_headers if f'<Simple value="{m}" />' in line), None)
            if found:
                current = found
            if current:
                results[current].append(line)

    # --- Step 2: Parse each section into a DataFrame ---
    if file_type == "Rules":
        excel_name = "ZXRules.xlsx"
    elif file_type == "Campaign":
        excel_name = "ZXCampaign.xlsx"
    else:
        print("Invalid file type")
        raise Exception

    excel_path = f"{ws}/{excel_name}"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for key, lines in results.items():
            rows = []
            headers = []
            current_row = []
            skip = False
            in_rows = False
            in_cols = False
            skip_first_item = False

            for line in lines:
                if '<Dictionary name="Cols"' in line:
                    in_cols = True
                    in_rows = False

                elif '<Dictionary name="Rows"' in line:
                    in_rows = True
                    in_cols = False

                elif in_cols and '<Simple value="' in line:
                    value = line.split('"', 2)[1]
                    if not skip:
                        headers.append(None if value == 'Null' else value)
                    skip = not skip

                elif in_rows and '<Item>' in line:
                    skip_first_item = True
                    if current_row:
                        rows.append(current_row)
                    current_row = []

                elif in_rows and '</Item>' in line:
                    if current_row:
                        rows.append(current_row)
                        current_row = []

                elif in_rows and '<Simple value="' in line:
                    if skip_first_item:
                        skip_first_item = False
                    else:
                        value = line.split('"', 2)[1]
                        current_row.append(value)

                elif in_rows and '<Null />' in line:
                    current_row.append("")

            if current_row:
                rows.append(current_row)

            # Create DataFrame and write to a sheet
            if headers and rows:
                df = pd.DataFrame(rows, columns=headers)
                df.to_excel(writer, sheet_name=key[:31], index=False)

    print(f"✅ Data successfully written to {excel_path}")


if __name__ in "__main__":
    generate_spreadhsheets(r'D:\Steam\steamapps\common\They Are Billions\ZXRules.dat')
    generate_spreadhsheets(r'D:\Steam\steamapps\common\They Are Billions\ZXCampaign.dat')