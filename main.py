__version__ = "0.1.0"

import json, sqlite3, logging, os
from datetime import datetime
import random, re, time, sys

import pandas as pd
import matplotlib.pyplot as plt
import sklearn
import tkinter as tk
import seaborn as sns
import numpy as np

class CreatingAssets():
    def __init__(self, db_path='assets.db', config_path='config.json', log_path='logs.log'):
        self.db_path = db_path
        self.config_path = config_path
        self.log_path = log_path

    def create_dir(self, path) -> None:
        """
        Creates a directory at the specified path if it does not already exist.

        Args:
            path (str): The path where the directory should be created.

        Returns:
            None

        Raises:
            OSError: If the directory cannot be created and does not already exist.
        """
        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.info(f"Assets created successfully at: {path}")

    def setup_logging(self) -> None:
        """
        Configures the logging settings for the application.

        Sets up the logging system to write log messages to the file specified by `self.log_path`
        in append mode. The log messages include the timestamp, log level, and message content.
        The logging level is set to INFO. Also initializes a logger instance named "User" and
        assigns it to `self.logger`.
        """
        logging.basicConfig(filename=self.log_path, filemode='a',
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger("User")
        return self.logger

    def setup_config(self) -> None:
        """
        Initializes or resets the configuration file at the specified path.

        This method opens the configuration file in write mode, effectively creating
        a new file or clearing the existing one. No content is written to the file.

        Raises:
            OSError: If the file cannot be opened for writing.
        """
        with open(self.config_path, 'w') as file:
            file.write(json.dumps({ # Here we used this way because when we use write method the method because it is in w mode it creates the config file
                "Version": __version__,
                "Creation_Date": str(datetime.now()),
            }, indent=4))

    def setup_db(self) -> None:
        """
        Creates a new, empty database file at the specified path.

        This method opens the file located at self.db_path in write mode, effectively creating
        the file if it does not exist or truncating it if it does. The file is left empty.
        """
        with open(self.db_path, 'w') as f:
            pass

class DbManager():
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns: dict) -> None:
        """
        Creates a new table in the database with the specified name and columns.

        Args:
            table_name (str): The name of the table to be created.
            columns (dict): A dictionary where keys are column names and values are their data types.

        Returns:
            None

        Raises:
            sqlite3.OperationalError: If there is an error executing the SQL command.
        """
        cols_with_types = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_with_types});"
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def insert_data(self, table_name, data: dict) -> None:
        """
        Inserts a new row of data into the specified table.

        Args:
            table_name (str): The name of the table where data should be inserted.
            data (dict): A dictionary where keys are column names and values are the corresponding data to insert.

        Returns:
            None

        Raises:
            sqlite3.OperationalError: If there is an error executing the SQL command.
        """
        cols = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders});"
        self.cursor.execute(insert_query, tuple(data.values()))
        self.conn.commit()

    def fetch_data(self, table_name, conditions=None) -> list:
        """
        Fetches rows of data from the specified table that meet the given conditions.

        Args:
            table_name (str): The name of the table to query.
            conditions (str, optional): A SQL WHERE clause to filter results. Defaults to None.
        """
        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def close_db(self) -> None:
        """
            Closes the database connection.
        """
        self.conn.close()

class JsonManager():

    def __init__(self, json_path: str = "config.json"):
        self.json_path = json_path

    def load_config(self):
        with open(self.json_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
            except FileNotFoundError:
                return "File not found"
        return data

    def save_config(self, data: dict):
        with open(self.json_path, "a", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

if __name__ == "__main__":

    MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(MAIN_DIR, 'assets')
    DB_PATH = os.path.join(ASSETS_DIR, 'assets.db')
    CONFIG_PATH = os.path.join(ASSETS_DIR, 'config.json')
    LOGS_PATH = os.path.join(ASSETS_DIR, 'logs.log')

    manager = CreatingAssets(DB_PATH, CONFIG_PATH, LOGS_PATH)
    manager.create_dir(ASSETS_DIR)
    manager.setup_db()
    logger = manager.setup_logging()
    manager.setup_config()