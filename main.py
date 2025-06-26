import logging
from fbref_client import FBRefClient
from table_parser import TableParser
from sheet_uploader import SheetUploader

def main():
    """I orchestrated the process of scraping, parsing, and uploading Premier League stats.

    Then I set up logging, initialized the necessary clients for scraping (FBRefClient), parsing
    (TableParser), and uploading (SheetUploader), then coordinate the workflow to fetch data
    from FBRef, parse it into DataFrames, and upload it to a Google Sheet. If no tables are
    found, log an error and exit.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    client = FBRefClient()
    parser = TableParser()
    uploader = SheetUploader()

    soup = client.get_soup()
    dfs, primary_squads = parser.parse_tables(soup)

    if not dfs:
        logging.error("No Premier League tables found to upload.")
        return

    uploader.upload_dataframes(dfs, primary_squads)

if __name__ == "__main__":
    main()