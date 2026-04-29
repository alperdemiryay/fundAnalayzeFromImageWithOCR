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
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpeg', '.jpg'))]
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

            data_list.append({
                'Time': timestamp,
                'Total Value': total_val,
                'Profit': profit_val
            })
            print(f"Processed {file}: {timestamp} -> Total: {total_val}, Profit: {profit_val}")

    return pd.DataFrame(data_list)


def plot_data(df):
    if df.empty:
        print("No data extracted.")
        return

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Total Value
    color = 'tab:blue'
    ax1.set_xlabel('Time of Day')
    ax1.set_ylabel('Total Portfolio Value (TL)', color=color)
    ax1.plot(df['Time'], df['Total Value'], marker='o', color=color, label='Total Value')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # Create second axis for Profit
    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Profit/Loss (TL)', color=color)
    ax2.plot(df['Time'], df['Profit'], marker='s', linestyle='--', color=color, label='Profit')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Portfolio Performance over Time')
    fig.tight_layout()
    plt.show()


# --- RUN ---
folder = "C:/Users/TCADEMIRYAY/PycharmProjects/fundAnalayzeFromImageWithOCR/images/"
df_results = process_portfolio_images(folder)
plot_data(df_results)