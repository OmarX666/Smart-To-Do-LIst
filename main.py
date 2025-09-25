__version__ = "0.1.0"

import json, sqlite3, logging, os
from datetime import datetime
import random, re, time, sys
from winreg import CreateKey

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
            Creates the assets directory
        """
        os.makedirs(self.assets_folder)

    def create_logging(self) -> None:
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

    def create_config(self) -> None:
        """
        Create config file
        """
        with open(self.config_path, 'w') as file:
            pass

    def create_db(self) -> None:
        """
        Create database file
        """

        with open(self.db_path, 'w') as f:
            pass

class DbManager():
    def __init__(self, db_path='UserInfo.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Enable foreign key constraints
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.conn.commit()

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

    def add_data(self, data_exist: dict = {}, data: dict = {}) -> None:
        """
        Adds new data to the existing JSON configuration.
        Args:
            data_exist (dict): A dictionary containing the existing data in Json file.
            data (dict): A dictionary containing the new data to be added.
        Returns:
            None
        """

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

class Setup_environment(DbManager, JsonManager):
    def __init__(self, db_path, config_path):
        DbManager.__init__(self, db_path)
        JsonManager.__init__(self, config_path)

        self.logger = logging.getLogger("setup_environment")
        self.logger.info("Environment setup completed")
        
    def setup_config(self) -> None:
        """ Setup config file """
                
        initial_config = {
            "Version": __version__,
            "Creation_Date": str(datetime.now()),
            "User_Data": {
                "ID": "",
                "Username": "",
                "Email": "",
                "Password": "",
            }
        }

        self.add_data(data_exist=initial_config)
        self.logger.info("Config file environment setup completed")

    def setup_db(self) -> None:
        """ Setup database file """

        self.create_table("users", {
            "ID": "INTEGER PRIMARY KEY",
            "Username": "TEXT NOT NULL UNIQUE",
            "Email": "TEXT NOT NULL UNIQUE",
            "Password": "TEXT NOT NULL",
        })

        self.create_table("Users_Tasks", {
            "Task_ID": "INTEGER PRIMARY KEY",
            "User_ID": "INTEGER NOT NULL",
            "Task_Name": "TEXT",
            "Description": "TEXT",
            "Priority": "TEXT",
            "Due_Date": "TEXT",
            "Status": "TEXT",
            "FOREIGN KEY (User_ID)": "REFERENCES users(ID)"
        })

        self.logger.info("Database file environment setup completed")

class SignUp():
    pass

class SignIn():
    pass


def main():
    """ Main function to run the application. """

    manager = CreatingAssets(ASSETS_DIR, DB_PATH, CONFIG_PATH, LOGS_PATH)

    if not os.path.exists(ASSETS_DIR) or \
    not os.path.exists(DB_PATH) or \
    not os.path.exists(CONFIG_PATH):

        manager.create_dir()
        manager.create_logging()
        manager.create_db()
        manager.create_config()

        setup_env = Setup_environment(DB_PATH, CONFIG_PATH)
        setup_env.setup_db()
        setup_env.setup_config()

    elif not os.path.exists(LOGS_PATH): # To avoid clearing Json file if logging file is not created
        manager.create_logging()


if __name__ == "__main__":

    MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(MAIN_DIR, 'assets')
    DB_PATH = os.path.join(ASSETS_DIR, 'UserInfo.db')
    CONFIG_PATH = os.path.join(ASSETS_DIR, 'config.json')
    LOGS_PATH = os.path.join(ASSETS_DIR, 'logs.log')

    main()