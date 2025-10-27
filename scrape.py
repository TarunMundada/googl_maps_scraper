from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time
import csv

# --- Setup Firefox ---
options = Options()
# options.add_argument("--headless")  # optional, remove if you want to see browser
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# --- Open Maps Search ---
url = "https://www.google.com/maps/search/plumbers+in+Lowell,+MA,+USA/@42.5400664,-71.203366,10z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI1MTAyMC4wIKXMDSoASAFQAw%3D%3D"
driver.get(url)
time.sleep(5)

# --- Scroll to load more results ---
scrollable_div_xpath = '//div[contains(@aria-label, "Results for") or contains(@aria-label, "Search results")]'
scrollable_div = driver.find_element("xpath", scrollable_div_xpath)

last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
same_count = 0
while same_count < 3:  # stop after no new items appear 3 times
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

# --- Extract Data ---
listings = soup.select("div.Nv2PK")
data = []

for listing in listings:
    name_tag = listing.select_one("a.hfpxzc")
    rating_tag = listing.select_one("span.MW4etd")
    phone_tag = listing.select_one("span.UsdlK")
    website_tag = listing.select_one("a[href^='http']")
    
    name = name_tag["aria-label"].strip() if name_tag else ""
    rating = rating_tag.get_text(strip=True) if rating_tag else ""
    phone = phone_tag.get_text(strip=True) if phone_tag else ""
    website = website_tag["href"] if website_tag else ""

    data.append({
        "Name": name,
        "Phone": phone,
        "Rating": rating,
        "Website": website
    })

# --- Save to CSV ---
with open("plumbers_lowell_ma.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Phone", "Rating", "Website"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ Saved {len(data)} results to electricians_lowell_ma.csv")

