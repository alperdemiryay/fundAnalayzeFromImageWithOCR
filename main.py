import cv2
import easyocr
import os
import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

# --- CONFIGURATION ---
FOLDER_PATH = "C:/Users/TCADEMIRYAY/PycharmProjects/fundAnalayzeFromImageWithOCR/images/"
DB_NAME = "fund_history.db"
CSV_NAME = "fund_history_export.csv"
RESET_DB = False

reader = easyocr.Reader(['tr', 'en'], gpu=False)


def init_db():
    if RESET_DB and os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("🗑️ Database reset. Re-processing images...")
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''CREATE TABLE IF NOT EXISTS fund_history 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT UNIQUE, 
                    timestamp DATETIME, total_val REAL, profit_amt REAL, profit_pct REAL)''')
    return conn


def get_image_time(file_path):
    filename = os.path.basename(file_path)
    # Extracts YYYY-MM-DD from filenames like '2026-02-15.PNG'
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d')
    return datetime.fromtimestamp(os.path.getmtime(file_path))


def clean_val(text):
    if not text: return 0.0
    cleaned = re.sub(r'[^0-9.,]', '', text)
    cleaned = cleaned.replace('.', '').replace(',', '.')
    try:
        return float(cleaned)
    except:
        return 0.0


def process_and_save():
    conn = init_db()
    cursor = conn.cursor()
    valid_exts = ('.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith(valid_exts)]
    files.sort()

    print(f"📁 Analyzing {len(files)} images...")

    for file in files:
        cursor.execute("SELECT id FROM fund_history WHERE filename = ?", (file,))
        if cursor.fetchone(): continue

        img = cv2.imread(os.path.join(FOLDER_PATH, file))
        if img is None: continue

        # Dynamic Crop (bottom 650px) and Upscale
        h, w = img.shape[:2]
        cropped = img[max(0, h - 650):h, 0:w]
        upscaled = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        results = reader.readtext(upscaled)
        full_text = " ".join([res[1] for res in results])

        # Parsing Profit (parentheses) and Total (money format)
        profit_search = re.search(r'\(\+?([\d\.]+,\d{2})', full_text)
        money_matches = re.findall(r'[\d\.]+,\d{2}', full_text)

        if profit_search and len(money_matches) >= 1:
            profit_amt = clean_val(profit_search.group(1))
            total_amt = clean_val(money_matches[0])

            # Correction if OCR catches a smaller number first
            if total_amt < profit_amt and len(money_matches) > 1:
                total_amt = clean_val(money_matches[1])

            cost = total_amt - profit_amt
            calc_pct = round((profit_amt / cost * 100), 2) if cost > 0 else 0.0
            file_time = get_image_time(os.path.join(FOLDER_PATH, file))

            cursor.execute('''INSERT INTO fund_history 
                            (filename, timestamp, total_val, profit_amt, profit_pct) 
                            VALUES (?, ?, ?, ?, ?)''',
                           (file, file_time, total_amt, profit_amt, calc_pct))
            print(f"✅ Processed {file}")

    conn.commit()
    conn.close()


def export_to_csv():
    """Reads all data from SQLite and dumps it into a CSV file."""
    conn = sqlite3.connect(DB_NAME)
    # Ordering by filename ensures chronological order for YYYY-MM-DD filenames
    df = pd.read_sql_query("SELECT * FROM fund_history ORDER BY filename ASC", conn)
    conn.close()

    if not df.empty:
        df.to_csv(CSV_NAME, index=False, encoding='utf-8-sig', sep=';')
        print(f"📄 Data successfully dumped to {CSV_NAME}")
    else:
        print("⚠️ No data available to export to CSV.")


def plot_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM fund_history ORDER BY filename ASC", conn)
    conn.close()
    if df.empty: return

    # Derive plotting date from filename
    df['plot_date'] = pd.to_datetime(df['filename'].str.extract(r'(\d{4}-\d{2}-\d{2})')[0])

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    fmt = plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)))

    ax1.plot(df['plot_date'], df['total_val'], 'o-', color='tab:blue', label='Total')
    ax2.plot(df['plot_date'], df['profit_amt'], 's-', color='tab:green', label='Profit')
    ax3.plot(df['plot_date'], df['profit_pct'], '^-', color='tab:red', label='Yield %')

    ax1.set_title('Total Fund Value (TL)', loc='left', fontweight='bold')
    ax2.set_title('Profit Amount (TL)', loc='left', fontweight='bold')
    ax3.set_title('Profit Percentage (%)', loc='left', fontweight='bold')

    for ax in [ax1, ax2]: ax.yaxis.set_major_formatter(fmt)
    for ax in [ax1, ax2, ax3]: ax.grid(True, alpha=0.3)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# --- MAIN EXECUTION ---
process_and_save()  # 1. Update DB from Images
export_to_csv()  # 2. Dump DB to CSV
plot_from_db()  # 3. Visualize