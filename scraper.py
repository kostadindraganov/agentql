import agentql
from agentql.async_api import ScrollDirection

import csv
from time import sleep  # Added for delay between page turns

from dotenv import load_dotenv

load_dotenv()

PRODUCTS = """
{
     casinos {
      casinos[]{
      casino_name
      rating
    }
  }
}
"""

NEXT_PAGE_BTN = """
{
    next_page_button_enabled
    next_page_button_disabled
}
"""


def main():
    session = None
    try:
        session = agentql.start_session("https://casinoguru-en.com/top-online-casinos#tab=ALL")
        session.driver.scroll_to_bottom()

        pagination = session.query(NEXT_PAGE_BTN)
        
        with open("product.csv", "a", newline="") as file:
            fieldnames = ["casino_name", "rating"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            while (
                pagination.to_data()["next_page_button_enabled"] 
                and pagination.to_data()["next_page_button_disabled"] is None
            ):
                products = session.query(PRODUCTS)
                for product in products.to_data()["results"]["products"]:
                    writer.writerow(product)

                pagination.next_page_button_enabled.click()
                session.driver.scroll_to_bottom()
                pagination = session.query(NEXT_PAGE_BTN)
                sleep(2)  # Delay between page turns (adjust as needed)

    except agentql.exceptions.QueryException as e:
        print(f"Error scraping products: {e}")
    finally:
        if session:
            session.stop()

if __name__ == "__main__":
    main()