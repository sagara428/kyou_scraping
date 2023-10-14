# lib/ingest_to_mysql.py
'''
Ingest to MySQL Module

This module provides functions to create a MySQL database,
ingest data from a CSV file into MySQL tables,
and perform SQL operations on the ingested data.

Functions:
    - create_and_ingest(output_file, config): Create and ingest data into MySQL tables.

Created tables:
    - product_details
    - product_wishlists_series

Dependencies:
    - CSV handling from csv
    - MySQL Connector from mysql.connector
'''
import csv
import mysql.connector


def create_and_ingest(output_file, config):
    '''
    Create and ingest data into MySQL tables.

    Created tables:
    - product_details
    - product_wishlists_series

    Args:
        output_file (str): Path to the CSV file containing data.
        config (dict): dictionary of MySQL configurations
    '''
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Create the kyou_scraping database if it doesn't exist
    cursor.execute('CREATE DATABASE IF NOT EXISTS kyou_scraping')
    cursor.execute('USE kyou_scraping')

    # Create the product_details table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS product_details (
        Title VARCHAR(255),
        Status VARCHAR(255),
        Price INT,
        Wishlist INT,
        `Character` VARCHAR(255),
        Series VARCHAR(255),
        Category VARCHAR(255),
        Manufacturer VARCHAR(255)
    )
    '''
    cursor.execute(create_table_query)

    # Commit the changes
    connection.commit()

    # Ingest the data from the CSV file into MySQL
    with open(output_file, 'r', newline='', encoding='utf-8') as file:
        csv_data = csv.DictReader(file)

        for row in csv_data:
            # Define the INSERT query
            insert_query = '''
            INSERT INTO product_details (Title, Status, Price, Wishlist, `Character`, Series, Category, Manufacturer)
            VALUES (%(Title)s, %(Status)s, %(Price)s, %(Wishlist)s, %(Character)s, %(Series)s, %(Category)s, %(Manufacturer)s)
            '''

            # Execute the INSERT query with data from the CSV
            cursor.execute(insert_query, row)

    # Commit the changes and close the cursor and connection
    connection.commit()

    # Create the product_wishlists_series table if it doesn't exist
    create_series_table_query = '''
    CREATE TABLE IF NOT EXISTS product_wishlists_series (
        Series VARCHAR(255),
        `Character` VARCHAR(255),
        Wishlist_Total INT,
        Average_Wishlist FLOAT
    )
    '''
    cursor.execute(create_series_table_query)
    connection.commit()

    # SQL query to insert data into the product_wishlists_series table
    insert_series_query = '''
    INSERT INTO product_wishlists_series (Series, `Character`, Wishlist_Total, Average_Wishlist)
    SELECT
        Series,
        `Character`,
        SUM(Wishlist) AS Wishlist_Total,
        AVG(SUM(Wishlist)) OVER (PARTITION BY Series) AS Average_Wishlist
    FROM product_details
    GROUP BY Series, `Character`
    ORDER BY Average_Wishlist DESC, Wishlist_Total DESC
    '''
    cursor.execute(insert_series_query)
    connection.commit()

    cursor.close()
    connection.close()
