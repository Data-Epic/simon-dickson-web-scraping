# Premier League Stats Uploader

A Python-based tool that scrapes Premier League statistics from FBRef, parses the data into structured DataFrames, and uploads them to a Google Sheet. The codebase is modularized into separate files for scraping, parsing, and uploading, ensuring clarity and maintainability.

## Features

- Scrapes Premier League statistics from FBRef using Selenium to handle dynamic content.
- Parses HTML tables into pandas DataFrames with comprehensive data cleaning.
- Handles 20 Premier League teams (Liverpool to Southampton) with aligned data.
- Comprehensive logging for debugging and monitoring.
- Robust error handling for network issues, Cloudflare challenges, and data inconsistencies.
- Configurable settings (e.g., URLs, credentials) in `config.py`.
- Adheres to PEP8 standards with detailed docstrings in all modules.

## Prerequisites

- Python 3.8+
- Google Cloud Platform service account credentials (JSON key file) for Google Sheets API access.
- Required libraries: `selenium`, `webdriver_manager`, `beautifulsoup4`, `lxml`, `pandas`, `gspread`, `oauth2client`

## Setup Instructions

1. **Clone the repository**:
```bash
git clone https://github.com/Data-Epic/simon-dickson-web-scraping.git
```

2. **Create a Virtual Environment**  
**On Mac/Linux OS**  
- Use the venv module to create a virtual environment (replace myenv with your preferred name):
```bash
python -m venv myenv
```
This creates a myenv directory containing the virtual environment.  
- Activate the virtual environment to isolate your Python environment:
```bash
source myenv/bin/activate
```

**On Windows OS**  
- Use the venv module to create a virtual environment (replace myenv with your preferred name):
```bash
python -m venv myenv
```
This creates a myenv directory containing the virtual environment.  
- Activate the virtual environment to isolate your Python environment:  
**In Command Prompt**:
```bash
myenv\Scripts\activate
```
**In PowerShell**:
```bash
.\myenv\Scripts\Activate.ps1
```
Your terminal prompt should change, indicating the virtual environment is active (e.g., (myenv)).

3. **Install Dependencies**  
With the virtual environment active, install the required packages using pip:
```bash
pip install selenium webdriver_manager beautifulsoup4 lxml pandas gspread oauth2client
```

4. **Set Up Google Sheets API Credentials**  
- Create a service account in the Google Cloud Console and download the JSON key file.
- Save the JSON key file as `credentials.json` in the project root directory.
- Update `config.py` with the path to your credentials file, the Google Sheet title, and your email:
```python
CREDENTIALS_PATH = "path/to/credentials.json"
SHEET_TITLE = "Premier League 2024-2025 stats"
MY_EMAIL = "your-service-account.iam.gserviceaccount.com"
FBREF_URL = "https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats"
```

## Usage Instructions

- Run the script as a Python module:
```bash
python main
```

## Example Output

The script will scrape data from FBRef, parse it, and upload it to a Google Sheet. The resulting sheet will look like this:

```
A1: Squad       B1: Home         C1: Home.1         D1: Home.2         E1: Home.3         F1: Home.4
A2: EPL Teams   B2: MP           C2: W              D2: D              E2: L              F2: GF
A3: Liverpool   B3: 17           C3: 14             D3: 2              E3: 1              F3: 39
A4: Arsenal     B4: 17           C4: 14             D4: 2              E4: 1              F4: 39
A5: Manchester City ...
...
A21: Leicester City B21: 18       C21: 3             D21: 3             E21: 12            F21: 13
A22: Southampton  B22: 17        C22: 1             D22: 2             E22: 14            F22: 12
```

The script logs the process, including the Google Sheet URL for easy access.


### Deactivate the Virtual Environment

When done, deactivate the virtual environment:
```bash
deactivate
```

### Requirements

- A valid Google Cloud service account JSON key file.
- An active internet connection for scraping and uploading.
- Chrome browser installed (required by Selenium for `webdriver_manager`).

### Future Improvements

- Add unit tests for each module to ensure reliability.
- Implement retry logic for Cloudflare challenges beyond the current retries.
- Support multiple seasons by dynamically adjusting the FBRef URL.
- Add data validation checks before uploading to Google Sheets.
- Include options to export data to other formats (e.g., CSV, Excel).
- Optimize performance by caching scraped data or using async requests.