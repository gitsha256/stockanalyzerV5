import pandas as pd
import glob
import os
import sys

# Resolve the snapshot CSV path
if len(sys.argv) > 1:
    latest_file = sys.argv[1]
else:
    snapshot_files = sorted([f for f in os.listdir(".") if f.endswith("snapshot.csv") and not f.endswith("snapshot_all.csv")])
    snapshot_all_files = sorted([f for f in os.listdir(".") if f.endswith("snapshot_all.csv")])

    if snapshot_files and snapshot_all_files:
        print("Choose snapshot source:")
        print("1. snapshot.csv")
        print("2. snapshot_all.csv")
        choice = input("Enter choice [default 1]: ").strip()
        if choice == '2':
            latest_file = snapshot_all_files[-1]
        else:
            latest_file = snapshot_files[-1]
    elif snapshot_files:
        latest_file = snapshot_files[-1]
    elif snapshot_all_files:
        latest_file = snapshot_all_files[-1]
    else:
        print("No snapshot file found in current directory.")
        sys.exit(1)

print(f"Using file: {latest_file}")

df = pd.read_csv(latest_file)
threshold = float(input("Enter the percent threshold (e.g., 5 for 5%): ")) / 100

# Drop rows with missing SMA or symbol values
sma_cols = ['s020', 's050', 's100', 's200', 'symb']
df = df.dropna(subset=sma_cols)

def all_near(row):
    sma200 = row['s200']
    if sma200 == 0:
        return False
    return (
        abs(row['s020'] - sma200) / sma200 <= threshold and
        abs(row['s050'] - sma200) / sma200 <= threshold and
        abs(row['s100'] - sma200) / sma200 <= threshold
    )

matching = df[df.apply(all_near, axis=1)]

# Save unique symbols to file
matching[['symb']].drop_duplicates().to_csv("sma.csv", index=False)
print(matching[['symb']].drop_duplicates())

print("Rows after dropna:", len(df))
print("Rows matching SMA confluence:", len(matching))
print("Threshold:", threshold)