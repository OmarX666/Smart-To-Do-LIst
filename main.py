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
    def __init__(self, assets_folder='assets', 
                 db_path='UserInfo.db', config_path='config.json', log_path='logs.log'):
        self.assets_folder = assets_folder
        self.db_path = db_path
        self.config_path = config_path
        self.log_path = log_path

    def create_dir(self) -> None:
        """
        Creates a directory at the specified path if it does not already exist.

        Args:
            path (str): The path where the directory should be created.

        Returns:
            None

        Raises:
            OSError: If the directory cannot be created and does not already exist.
        """
        if not os.path.exists(self.assets_folder):
            os.makedirs(self.assets_folder)

    def setup_logging(self) -> None:
        """
        Configures the logging settings for the application.

        Sets up the logging system to write log messages to the file specified by `self.log_path`
        in append mode. The log messages include the timestamp, log level, and message content.
        The logging level is set to INFO. Also initializes a logger instance named "User" and
        assigns it to `self.logger`.
        """
        logging.basicConfig(filename=self.log_path, filemode='a',
                            format='%(asctime)s - %(levelname)s [ %(message)s ]',
                            datefmt="%Y-%m-%d %H:%M:%S",
                            level=logging.INFO)

    def setup_config(self) -> None:
        """
        Initializes or resets the configuration file at the specified path.

        This method opens the configuration file in write mode, effectively creating
        a new file or clearing the existing one. No content is written to the file.

        Raises:
            OSError: If the file cannot be opened for writing.
        """
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as file:
                file.write(json.dumps({ # Here we used this way because when we use write method the method because it is in w mode it creates the config file
                    "Version": __version__,
                    "Creation_Date": str(datetime.now()),
                    "User_Data":{
                        "ID": "",
                        "Username": "",
                        "Email": "",
                        "Password": "",
                    },
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
    def __init__(self, db_path='UserInfo.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.logger = logging.getLogger("DbManager")

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
        self.logger = logging.getLogger("JsonManager")

    def load_config(self) -> dict:
        """
        Loads and returns the JSON configuration from the specified file.
        Returns:
            dict: The JSON data as a dictionary. If the file is empty or an error occurs
        """
        with open(self.json_path, "r") as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError as JSOND:
                print("Reading From Empty File.")
                data = {"Error": JSOND}
            except Exception as Error:
                print("Error Happened.")
                data = {"Error": Error}
            finally:
                self.logger.info("Config Loaded.")
                return data

    def add_data(self, data: dict) -> None:
        """
        Adds new data to the existing JSON configuration.
        Args:
            data (dict): A dictionary containing the new data to be added.
        Returns:
            None
        """
        data_exist = self.load_config()
        data_exist.update(data)
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(data_exist, file, indent=4)
        self.logger.info("Config Updated.")

    def delete_data(self, key: str) -> None:
        """
        Deletes a key-value pair from the JSON configuration based on the provided key.
        Args:
            key (str): The key to be deleted from the configuration.
        Returns:
            None
        """
        data_exist = self.load_config()
        if key in data_exist:
            del data_exist[key]
            with open(self.json_path, "w", encoding="utf-8") as file:
                json.dump(data_exist, file, indent=4)
            self.logger.info("Key Deleted From Config.")
        else:
            self.logger.warning("Key Not Found In Config.")

class SignUp():
    pass

class SignIn():
    pass


def main():
    """ Main function to run the application. """
    MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(MAIN_DIR, 'assets')
    DB_PATH = os.path.join(ASSETS_DIR, 'UserInfo.db')
    CONFIG_PATH = os.path.join(ASSETS_DIR, 'config.json')
    LOGS_PATH = os.path.join(ASSETS_DIR, 'logs.log')

    manager = CreatingAssets(ASSETS_DIR, DB_PATH, CONFIG_PATH, LOGS_PATH)
    manager.create_dir()
    manager.setup_db()
    manager.setup_logging()
    manager.setup_config()

if __name__ == "__main__":
    main()