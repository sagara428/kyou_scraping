'''
Main script to scrape data from kyou.id,
save it to a CSV file,
and ingest it into a MySQL database.
'''
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from lib.kyou_scraper import extract_product_urls, scrape_product_details
from lib.ingest_to_mysql import create_and_ingest

def main():
    '''
    Main function to perform the scraping, saving to a CSV file, and database ingestion
    '''
    # Set up the Chrome web driver
    driver = webdriver.Chrome()

    root = 'https://kyou.id'
    total_pages = 25

    # Initialize a list to store the product URLs
    data = []

    # Loop through all pages to extract product URLs
    for page_number in range(1, total_pages + 1):
        page_url = f'{root}/search?q=&sort=wishlists&page={page_number}%2C40'
        driver.get(page_url)

        try:
            extract_product_urls(driver, data)

            # Scroll down to trigger lazy loading
            for _ in range(10):  # Adjust the number of scrolls as needed
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(3)  # Wait for the page to load (adjust as needed)
        except NoSuchElementException:
            print(f'Reached the last page: {page_number}')
            break

    # Initialize a list to store product details
    product_details = []

    # Loop through the product URLs and scrape details
    for product_url in data:
        details = scrape_product_details(driver, product_url, root)
        product_details.append(details)

    # Close the web driver
    driver.quit()

    # Output to csv before ingest to mysql
    # Filter out items with status "Prototype Showcase" since it is not needed (0 price)
    product_details = [product for product in product_details if product['Status'] != 'Prototype Showcase']

    # Write the product details to a CSV file
    output_file = 'product_details.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(
            file, fieldnames=['Title', 'Status',
                              'Price', 'Wishlist',
                              'Character', 'Series',
                              'Category', 'Manufacturer'
            ]
        )
        writer.writeheader()
        writer.writerows(product_details)

    print(f'Details saved to {output_file}')

    # Ingest data into MySQL
    # MySQL config
    config = {
        'user': 'root', # Change to your MySQL user
        'password': 'ghjuybbn', # Change to your password
        'host': 'localhost', # Change to your host
    }
    create_and_ingest(output_file, config)

if __name__ == '__main__':
    main()
