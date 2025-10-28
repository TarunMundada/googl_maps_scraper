from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time
import csv

# --- Setup Firefox ---
options = Options()
# options.add_argument("--headless")  # comment this line if you want to see the browser
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# --- Open Google Maps Search ---
url = "https://www.google.com/maps/search/carpenter+in+Washington+D.C.,+DC,+USA"
driver.get(url)
time.sleep(6)

# --- Scroll to load all results ---
scrollable_div_xpath = '//div[contains(@aria-label, "Results for") or contains(@aria-label, "Search results")]'
scrollable_div = driver.find_element("xpath", scrollable_div_xpath)

last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
same_count = 0
while same_count < 3:  # stop after 3 scrolls with no change
    driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
    time.sleep(3)
    new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    if new_height == last_height:
        same_count += 1
    else:
        same_count = 0
    last_height = new_height

# --- Parse full HTML ---
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# --- Extract listings ---
listings = soup.select("div.Nv2PK")
data = []

for listing in listings:
    # --- Basic info ---
    name_tag = listing.select_one("a.hfpxzc")
    rating_tag = listing.select_one("span.MW4etd")
    reviews_tag = listing.select_one("span.UY7F9")
    address_tag = listing.select_one("div.W4Efsd span.W4Efsd") 
    phone_tag = listing.select_one("span.UsdlK")

    # --- Website ---
    website_link = ""
    for a_tag in listing.select("a"):
        href = a_tag.get("href", "")
        if href and "google.com" not in href and href.startswith("http"):
            website_link = href
            break

    # --- Extract values ---
    name = name_tag["aria-label"].strip() if name_tag else ""
    rating = rating_tag.get_text(strip=True) if rating_tag else ""
    reviews = reviews_tag.get_text(strip=True) if reviews_tag else ""
    phone = phone_tag.get_text(strip=True) if phone_tag else ""
    address = address_tag.get_text(strip=True) if address_tag else ""

    # Combine rating and reviews: e.g. "4.7 (23)"
    rating_full = f"{rating} {reviews}".strip()

    data.append({
        "Name": name,
        "Phone": phone,
        "Rating": rating_full,
        "Address": address,
        "Website": website_link
    })

# --- Save to CSV ---
with open("carpenter_dc.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Phone", "Rating", "Address", "Website"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ Saved {len(data)} results to electricians_lowell_ma.csv")