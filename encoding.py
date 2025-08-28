import pandas as pd
from ftfy import fix_text
import os
import re

INPUT = "data/Pankow_2024.csv"
OUTPUT = "data/Pankow_2024_utf8.csv"

def repair_csv(path: str, out_path: str):
    print(f"👉 Repairing {path} → {out_path}")
    df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")

    # Step 1: fix mojibake with ftfy
    for i, col in enumerate(df.select_dtypes(include=["object"]).columns, start=1):
        print(f"   [{i}] Fixing column: {col}")
        df[col] = df[col].map(lambda x: fix_text(x) if isinstance(x, str) else x)

    # Step 2: remove stray "¬" and normalize spacing
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = (
            df[col]
            .str.replace("¬", "", regex=False)      # remove the character
            .str.replace(r"\s+", " ", regex=True)   # collapse multiple spaces
            .str.strip()                            # trim start/end spaces
        )

    # Save clean UTF-8
    df.to_csv(out_path, encoding="utf-8", index=False)
    print(f"✅ Saved repaired file: {out_path}\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT):
        print(f"❌ File not found: {INPUT}")
    else:
        repair_csv(INPUT, OUTPUT)
        print("🎉 Done!")