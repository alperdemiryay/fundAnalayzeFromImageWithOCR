import cv2
import easyocr
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize OCR (Turkish and English)
reader = easyocr.Reader(['tr', 'en'])


def clean_number(text):
    """Converts Turkish formatted strings (1.234,56) to float (1234.56)"""
    if not text: return 0.0
    # Remove dots (thousands separator) and replace comma with dot (decimal)
    cleaned = text.replace('.', '').replace(',', '.')
    # Extract only numbers, dots, and signs
    cleaned = re.sub(r'[^0-9.\-]', '', cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def process_portfolio_images(folder_path):
    data_list = []

    # Get all jpeg files
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpeg', '.jpg', '.png'))]
    # Sorting by name usually helps keep them in chronological order
    files.sort()

    print(f"Found {len(files)} images. Starting OCR...")

    for file in files:
        img_path = os.path.join(folder_path, file)
        results = reader.readtext(img_path)

        full_text = " ".join([res[1] for res in results])
        try:
            full_text = full_text.split('Bank')[1]
        except:
            pass

        # 1. Extract Time (Top left usually)
        # Looking for HH:MM pattern
        time_match = re.search(r'(\d{2}:\d{2})', full_text)
        timestamp = time_match.group(1) if time_match else file

        # 2. Extract Values
        # We look for the pattern: Top. Değer / Kâr Zarar(TL)
        # In your screenshots, they appear as "TotalValue / ProfitValue"
        # Logic: Find the line that looks like money (digits with dots and commas)

        money_pattern = r'(\d{1,3}(?:\.\d{3})*,\d{2})'
        matches = re.findall(money_pattern, full_text)

        if len(matches) >= 2:
            # Usually, the first two large numbers in that section are Total and Profit
            # Based on your UI: Top. Değer is the first, Profit is the second
            total_val = clean_number(matches[-2])
            profit_val = clean_number(matches[-1])
            
            cost = total_val - profit_val
            profit_pct = round((profit_val / cost * 100), 2) if cost > 0 else 0.0

            data_list.append({
                'Time': timestamp,
                'Total Value': total_val,
                'Profit': profit_val,
                'Profit Percentage': profit_pct
            })
            print(f"Processed {file}: {timestamp} -> Total: {total_val}, Profit: {profit_val}, %: {profit_pct}")

    return pd.DataFrame(data_list)


def plot_data(df):
    if df.empty:
        print("No data extracted.")
        return

    # --- FIGURE 1: Actual Values ---
    fig1, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    fmt = plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)))

    ax1.plot(df['Time'], df['Total Value'], 'o-', color='tab:blue', label='Total')
    ax2.plot(df['Time'], df['Profit'], 's-', color='tab:green', label='Profit')
    ax3.plot(df['Time'], df['Profit Percentage'], '^-', color='tab:red', label='Yield %')

    ax1.set_title('Total Fund Value (TL)', loc='left', fontweight='bold')
    ax2.set_title('Profit Amount (TL)', loc='left', fontweight='bold')
    ax3.set_title('Profit Percentage (%)', loc='left', fontweight='bold')

    for ax in [ax1, ax2]: ax.yaxis.set_major_formatter(fmt)
    for ax in [ax1, ax2, ax3]: ax.grid(True, alpha=0.3)

    fig1.autofmt_xdate(rotation=45)
    fig1.tight_layout()
    plt.show()

    # --- FIGURE 2: Differences ---
    df_diff = df.copy()
    df_diff['Total Value Diff'] = df['Total Value'].diff()
    df_diff['Profit Diff'] = df['Profit'].diff()
    df_diff['Profit Percentage Diff'] = df['Profit Percentage'].diff()

    fig2, (ax4, ax5, ax6) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

    # Plotting diffs as bars (green for positive, red for negative)
    colors_total = ['tab:green' if val >= 0 else 'tab:red' for val in df_diff['Total Value Diff']]
    colors_profit = ['tab:green' if val >= 0 else 'tab:red' for val in df_diff['Profit Diff']]
    colors_pct = ['tab:green' if val >= 0 else 'tab:red' for val in df_diff['Profit Percentage Diff']]

    ax4.bar(df_diff['Time'], df_diff['Total Value Diff'], color=colors_total)
    ax4.axhline(0, color='black', linewidth=1)
    
    ax5.bar(df_diff['Time'], df_diff['Profit Diff'], color=colors_profit)
    ax5.axhline(0, color='black', linewidth=1)
    
    ax6.bar(df_diff['Time'], df_diff['Profit Percentage Diff'], color=colors_pct)
    ax6.axhline(0, color='black', linewidth=1)

    ax4.set_title('Total Fund Value Difference (TL)', loc='left', fontweight='bold')
    ax5.set_title('Profit Amount Difference (TL)', loc='left', fontweight='bold')
    ax6.set_title('Profit Percentage Difference (%)', loc='left', fontweight='bold')

    for ax in [ax4, ax5]: ax.yaxis.set_major_formatter(fmt)
    for ax in [ax4, ax5, ax6]: ax.grid(True, alpha=0.3, axis='y')

    fig2.autofmt_xdate(rotation=45)
    fig2.tight_layout()
    plt.show()


# --- RUN ---
folder = "C:/Users/TCADEMIRYAY/PycharmProjects/fundAnalayzeFromImageWithOCR/images/"
df_results = process_portfolio_images(folder)
plot_data(df_results)