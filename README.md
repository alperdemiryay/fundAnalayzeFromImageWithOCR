# Fund Analyze From Image With OCR

This project is a Python-based tool that uses Optical Character Recognition (OCR) to automatically extract financial data (such as total fund value and profit amount) from screenshots of your portfolio. It tracks your fund history over time, saves the data to a database, exports it to CSV, and generates visualizations of your portfolio's performance.

## 🌟 Features

* **Automated Data Extraction**: Uses `easyocr` and `opencv` to read total portfolio values and profit/loss amounts from images.
* **Date Tracking**: Automatically determines the date of the screenshot from its filename (e.g., `2026-02-15.PNG`) or its file creation time.
* **Database Storage**: Stores all historical data persistently in an SQLite database (`fund_history.db`).
* **CSV Export**: Automatically exports the database contents to a CSV file (`fund_history_export.csv`) for easy viewing and spreadsheet integration.
* **Data Visualization**: Generates clear, annotated plots showing Total Fund Value, Profit Amount, and Profit Yield Percentage over time.

## 📁 Project Structure

* `main.py`: The main script that processes images, saves to the database, exports to CSV, and visualizes the data.
* `main2.py`: An alternative script for quick processing and plotting without persistent database storage.
* `images/`: The directory where you should place your portfolio screenshots (supports `.png`, `.jpg`, `.jpeg`).
* `fund_history.db`: SQLite database generated automatically to store historical data.
* `fund_history_export.csv`: Exported CSV file containing your parsed data.

## 🚀 Prerequisites

To run this project, you need to have Python 3.x installed along with the following libraries:

```bash
pip install opencv-python easyocr pandas matplotlib
```

## 🛠️ How to Use

1. **Add Images**: Place your portfolio screenshots in the `images/` folder. For best results, name them with the date format `YYYY-MM-DD.png` (e.g., `2026-02-15.png`).
2. **Run the Script**: Execute the main script to process the images.
   ```bash
   python main.py
   ```
3. **View Results**: 
   * The script will output its progress in the terminal.
   * Check `fund_history_export.csv` for the raw extracted data.
   * A plot will automatically open showing your fund's historical performance.

## ⚙️ Configuration (Optional)

In `main.py`, you can modify the following configuration variables at the top of the script:
* `FOLDER_PATH`: Change the directory where images are read from.
* `RESET_DB`: Set to `True` if you want to wipe the existing database and re-process all images from scratch.
