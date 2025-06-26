import logging
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from config import CREDENTIALS_PATH, SHEET_TITLE, MY_EMAIL

class SheetUploader:
    """To upload pandas DataFrames to a Google Sheet with a specific format.

    I authenticated with Google Sheets API, merged DataFrames with a primary Squad column,
    and uploaded them to separate worksheets. Then, I formatted the output with "EPL Teams" in cell A2,
    team names from A3 to A22, and shift data accordingly, ensuring no row 23 is created.
    """
    def __init__(self):
        """I initialized the SheetUploader with the necessary API scope and authenticated.

        I defined the scope for Google Sheets and Drive APIs and authenticated using
        service account credentials.
        """
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.client = self.authenticate()

    def authenticate(self):
        """To authenticate with the Google Sheets API using service account credentials.

        Returns:
            gspread.Client: The authenticated gspread client.

        Raises:
            Exception: If authentication fails.
        """
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, self.scope)
            return gspread.authorize(creds)
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            raise

    def upload_dataframes(self, dfs, primary_squads):
        """To upload a list of DataFrames to a Google Sheet with specific formatting.

        I opened or created a Google Sheet, shared it with specified emails, and uploaded each
        DataFrame to a separate worksheet. Then, I merged the primary Squad column, formatted the
        output with "EPL Teams" in A2, list teams from A3 to A22, and shift data up to
        avoid row 23.

        Args:
            dfs (list of tuple): List of (table_name, DataFrame) pairs to upload.
            primary_squads (list): List of team names to use as the primary Squad column.

        Raises:
            Exception: If the upload process fails.
        """
        logging.info(f"Uploading {len(dfs)} DataFrames to Google Sheet: {SHEET_TITLE}")
        
        try:
            try:
                spreadsheet = self.client.open(SHEET_TITLE)
                logging.info(f"Found existing sheet: {SHEET_TITLE}")
            except gspread.exceptions.SpreadsheetNotFound:
                logging.info(f"Creating new sheet: {SHEET_TITLE}")
                spreadsheet = self.client.create(SHEET_TITLE)

            spreadsheet.share(MY_EMAIL, perm_type='user', role='writer')
            spreadsheet.share('simonoche987@gmail.com', perm_type='user', role='writer')
            logging.info(f"Sheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")

            for table_name, df in dfs:
                if df.empty:
                    logging.error(f"DataFrame for {table_name} is empty. Skipping.")
                    continue

                if primary_squads is not None:
                    merged_df = pd.DataFrame({'Squad': primary_squads})
                    if 'Squad' in df.columns:
                        merged_df = merged_df.merge(df.drop(columns=['Squad'], errors='ignore'), 
                                                  left_on='Squad', 
                                                  right_on=df['Squad'] if 'Squad' in df.columns else None, 
                                                  how='left')
                    else:
                        merged_df = pd.concat([merged_df, df.reset_index(drop=True)], axis=1)
                    for col in merged_df.columns:
                        if col != 'Squad':
                            if merged_df[col].dtype in ['float64', 'int64']:
                                merged_df[col] = merged_df[col].fillna(0)
                            else:
                                merged_df[col] = merged_df[col].fillna("")
                    merged_df = merged_df.where(pd.notnull(merged_df), None)
                else:
                    merged_df = df
                    logging.warning(f"No primary Squad column available for {table_name}; using original DataFrame")

                if 'Squad' in merged_df.columns:
                    headers = merged_df.columns.tolist()
                    data_values = merged_df.values.tolist()
                    squad_idx = headers.index('Squad')
                    final_data = [headers]
                    if data_values and all(row is not None for row in data_values) and len(data_values) > 1:
                        row_2 = ["EPL Teams" if i == squad_idx else data_values[0][i] for i in range(len(headers))]
                        final_data.append(row_2)
                        max_rows = min(20, len(data_values) - 1)
                        for i in range(max_rows):
                            row_data = [primary_squads[i] if j == squad_idx else data_values[i+1][j] for j in range(len(headers))]
                            final_data.append(row_data)
                    else:
                        logging.warning(f"No valid data rows in DataFrame for {table_name}. Adding 'EPL Teams' header only.")
                        final_data.append(["EPL Teams" if i == squad_idx else None for i in range(len(headers))])
                else:
                    final_data = [merged_df.columns.tolist()] + merged_df.values.tolist()

                safe_sheet_name = table_name.replace('/', '_').replace(':', '_')[:31]
                
                try:
                    worksheet = spreadsheet.worksheet(safe_sheet_name)
                    logging.info(f"Found existing worksheet: {safe_sheet_name}")
                except gspread.exceptions.WorksheetNotFound:
                    logging.info(f"Creating new worksheet: {safe_sheet_name}")
                    worksheet = spreadsheet.add_worksheet(title=safe_sheet_name, rows=100, cols=20)

                worksheet.update(final_data)
                logging.info(f"Uploaded {table_name} to worksheet {safe_sheet_name}.")

            worksheets = spreadsheet.worksheets()
            if len(worksheets) > 1:
                try:
                    sheet1 = spreadsheet.worksheet("Sheet1")
                    spreadsheet.del_worksheet(sheet1)
                    logging.info("Deleted default 'Sheet1' worksheet.")
                except gspread.exceptions.WorksheetNotFound:
                    logging.info("No 'Sheet1' worksheet found to delete.")
            else:
                logging.info("Not deleting 'Sheet1' as it's the only worksheet.")

        except Exception as e:
            logging.error(f"Failed to upload to Google Sheet: {e}")
            raise