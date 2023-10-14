# lib/kyou_scraper.py
'''
Kyou Scraper Module

This module provides functions to scrape product URLs and details from the
kyou.id website using Selenium and BeautifulSoup.

Functions:
    - extract_product_urls(driver, data): Extract product URLs from a web page.
    - scrape_product_details(driver, product_url, web): Scrape product details
      from a product page and clean them.

Dependencies:
    - BeautifulSoup from bs4
    - Selenium WebDriver from selenium
'''
from bs4 import BeautifulSoup

def extract_product_urls(driver, data):
    '''
    Extract product URLs from the given web page using BeautifulSoup.

    :param driver: The Selenium WebDriver.
    :param data: List to store the extracted product URLs.
    '''
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    product_elements = soup.select('li.indexstyled__InfoName-sc-1vqzqkx-8.gtnUZH a')

    for product_element in product_elements:
        product_url = product_element['href']
        data.append(product_url)


def scrape_product_details(driver, product_url, web):
    '''
    Scrape product details from the given product URL and clean them.

    :param driver: The Selenium WebDriver.
    :param product_url: URL of the product page.
    :param web: Root URL of the website.
    :return: Dictionary containing cleaned scraped product details.
    '''
    driver.get(f'{web}{product_url}')
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')


    def clean_title(title):
        # Remove extra whitespace
        return ' '.join(title.split())


    def clean_price(price):
        # Extract and cast the price to an integer
        price = price.replace('IDR', '').split('Earn')[0].strip()
        price = int(price.replace(',', '').strip())

        return price


    def clean_wishlist(wishlist):
        # Extract and cast the wishlist count to an integer
        return int(wishlist.split('Wishlist')[0].strip())

    # select and clean title, status, price, wishlist, character
    # series, category, and manufacturer details of product
    title_selector = (
        '#__next > div.transition > div > div > div > div > '
        'div > div.product-view > div > div.product-view__content__info > '
        'div.product-view__content__header > div > h2'
    )
    title = clean_title(soup.select_one(title_selector).text.strip())

    status_selector = (
        '#__next > div.transition > div > div > div > div > '
        'div > div.product-view > div > div.product-view__content__info > '
        'div.product-view__content__header > div > div > span'
    )
    status = soup.select_one(status_selector).text.strip()

    price_selector = (
        '#__next > div.transition > div > div > div > div > '
        'div > div.product-view > div > div.product-view__content__info > '
        'div.product-view__content__price-info > div:nth-child(1) > span'
    )
    price_element = soup.select_one(price_selector)
    price = clean_price(price_element.text.strip()) if price_element else None

    wishlist_selector = '#AddtoWishlist > span'
    wishlist_element = soup.select_one(wishlist_selector)
    wishlist = clean_wishlist(wishlist_element.text.strip()) if wishlist_element else None

    character_selector = (
        '#__next > div.transition > div > div > div > div > '
        'div > div.product-view > div > div.product-view__content__info > '
        'div.product-view__content__item-detail > ul > li:nth-child(1) > div > a'
    )
    character_element = soup.select_one(character_selector)
    character = clean_title(character_element.text.strip()) if character_element else None

    series_selector = (
        '#__next > div.transition > div > div > div > div > '
        'div > div.product-view > div > div.product-view__content__info > '
        'div.product-view__content__item-detail > ul > li:nth-child(2) > div > a'
    )
    series_element = soup.select_one(series_selector)
    series = clean_title(series_element.text.strip()) if series_element else None

    category_selector = (
        '#__next > div.transition > div > div > div > div > '
        'div > div.product-view > div > div.product-view__content__info > '
        'div.product-view__content__item-detail > ul > li:nth-child(3) > div > a'
    )
    category_element = soup.select_one(category_selector)
    category = clean_title(category_element.text.strip()) if category_element else None

    manufacturer_selector = (
        '#__next > div.transition > div > div > div > div > '
        'div > div.product-view > div > div.product-view__content__info > '
        'div.product-view__content__item-detail > ul > li:nth-child(4) > div > a'
    )
    manufacturer_element = soup.select_one(manufacturer_selector)
    manufacturer = clean_title(manufacturer_element.text.strip()) if manufacturer_element else None

    return {
        'Title': title,
        'Status': status,
        'Price': price,
        'Wishlist': wishlist,
        'Character': character,
        'Series': series,
        'Category': category,
        'Manufacturer': manufacturer,
    }
