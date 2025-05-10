import pandas as pd
import logging
from io import StringIO

class TableParser:
    """To parse HTML tables into pandas DataFrames and extract the primary Squad column.

    I processed HTML tables from a BeautifulSoup object, focusing on Premier League-related
    tables, and clean the resulting DataFrames. I also identified and extracted the primary
    Squad column from the main Premier League table for use in other classes.
    """
    def parse_tables(self, soup):
        """To parse HTML tables from a BeautifulSoup object into DataFrames.

        I iterated through all tables in the provided BeautifulSoup object, filter for
        Premier League tables, parse them into DataFrames, and clean them. Then, I extracted the
        primary Squad column from the main Premier League table if available.

        Args:
            soup (BeautifulSoup): The parsed HTML content containing tables.

        Returns:
            tuple: A list of (table_name, DataFrame) pairs and the primary_squads list.
        """
        tables = soup.find_all("table")
        dfs = []
        primary_squads = None

        for table in tables:
            caption = table.find("caption")
            table_name = caption.get_text().strip() if caption else table.get("id", "StatsTable")

            if "Premier League" not in table_name:
                logging.info(f"Skipping non-Premier League table: {table_name}")
                continue

            try:
                html_str = str(table)
                df = pd.read_html(StringIO(html_str), header=0)[0]
            except ValueError:
                logging.warning(f"Could not parse table {table_name}. Skipping.")
                continue

            cleaned_df = self.clean_dataframe(df)
            
            if "Premier League Table" in table_name and primary_squads is None:
                if 'Squad' in cleaned_df.columns:
                    primary_squads = cleaned_df['Squad'].copy()
                    logging.info(f"Extracted primary Squad column from {table_name} with {len(primary_squads)} teams")
                else:
                    logging.warning(f"Primary table {table_name} lacks Squad column")
            
            dfs.append((table_name, cleaned_df))

        return dfs, primary_squads

    def clean_dataframe(self, df):
        """To clean a pandas DataFrame by removing unwanted columns and formatting data.

        I removed unnamed columns, drop the 'Rk' column if present, strip whitespace from
        column names and string values, standardize the 'Squad' column name, clean team names,
        and handle missing values by filling numeric columns with 0 and string columns with
        an empty string.

        Args:
            df (pandas.DataFrame): The DataFrame to clean.

        Returns:
            pandas.DataFrame: The cleaned DataFrame.
        """
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        if "Rk" in df.columns:
            df = df.drop(columns=["Rk"])
        df.columns = [col.strip() for col in df.columns]
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        squad_column = None
        for col in df.columns:
            if col.lower() in ['squad', 'team', 'club']:
                squad_column = col
                break
        if squad_column and squad_column != 'Squad':
            df = df.rename(columns={squad_column: 'Squad'})
            logging.info(f"Renamed column '{squad_column}' to 'Squad'")
        elif not squad_column and 'Squad' not in df.columns:
            logging.warning("No 'Squad' or similar column found in DataFrame")
        if 'Squad' in df.columns:
            df['Squad'] = df['Squad'].str.replace(r'[\*\†]', '', regex=True)
            df = df[df['Squad'].notna() & ~df['Squad'].str.contains('Average|Total', case=False, na=False)]
            df = df[df['Squad'].str.strip() != '']
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("")
        return df