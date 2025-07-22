# Receipt & Bill Processing Mini-Application

A full-stack solution for uploading, parsing, and analyzing receipts and bills (e.g., electricity, internet, groceries). The system extracts structured data using rule-based logic and/or OCR, then presents summarized insights such as total spend, top vendors, and billing trends. The focus is on robust backend algorithms (search, sort, aggregation) and an interactive, modern UI.

## Features
- **Multi-format Upload:** Supports JPG, PNG, PDF, and TXT files
- **Data Extraction:** Vendor, date, amount, category, currency, language
- **Rule-based & OCR Parsing:** Uses Tesseract OCR and regex rules
- **Database Storage:** SQLite with ACID compliance and indexing
- **Search & Filter:** Keyword, pattern, and range-based search
- **Sorting & Aggregation:** Custom quicksort, sum, mean, median, mode, time-series
- **Analytics Dashboard:** Visualizations (bar, pie, line, treemap) for spending trends
- **Manual Corrections:** Edit parsed data via the UI
- **Export:** Download data as CSV or JSON
- **Multi-currency & Multi-language:** Detection and analytics

## Requirements
- Python 3.8+
- See `requirements.txt` for all dependencies

## Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Install Tesseract OCR for image parsing:
   - Windows: Download from https://github.com/tesseract-ocr/tesseract
   - Linux: `sudo apt-get install tesseract-ocr`

## Usage
1. Run the Streamlit app:
   ```bash
   streamlit run app2.py
   ```
2. Open your browser to the provided local URL.
3. Use the top navigation tabs to:
   - Upload and process receipts
   - View analytics dashboard
   - Search, filter, and export data
   - Edit/correct parsed receipts
   - Manage settings and database

## Project Structure
```
├── app2.py            # Streamlit frontend
├── receipt_processor.py # Backend processing and algorithms
├── database.py        # Database access and management
├── algorithms.py      # Sorting, searching, aggregation algorithms
├── requirements.txt   # Python dependencies
├── .gitignore         # Git ignore file
├── README.md          # This file
```

## Notes
- All data is stored locally in `my_receipts.db` (SQLite).
- For OCR, Tesseract must be installed and available in your PATH.
- For best results, upload clear, high-resolution images or PDFs.

---

**Built with Python, Streamlit, Pandas, Plotly, and SQLite.** 