from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import os
import time

# --- CONFIGURATION ---
# Add your Streamlit app URLs here in the list
DEFAULT_URLS = [
    "https://hyperops-dyu5cgjkrxdr5gnralziv4.streamlit.app/",
    # Add more links below like this:
    "https://hyperops-evgqdzzaj8rg8awsjvm4dp.streamlit.app/",
    "https://hyperops-c7ygrqpuvxudrx6pfrsc3d.streamlit.app/",
    "https://hyperops-telligqtw4eklqwcmbs6nx.streamlit.app/"
]

def get_urls():
    """
    Retrieves URLs from environment variable 'STREAMLIT_APP_URLS' (comma-separated)
    or falls back to the DEFAULT_URLS list defined above.
    """
    env_urls = os.environ.get("STREAMLIT_APP_URLS")
    if env_urls:
        # Split by comma and strip whitespace so you can pass "url1, url2" in env vars
        return [url.strip() for url in env_urls.split(",") if url.strip()]
    return DEFAULT_URLS

def wake_up_app(driver, url):
    """
    Visits a single URL and attempts to click the wake-up button.
    """
    print(f"--------------------------------------------------")
    print(f"Checking: {url}")
    
    try:
        driver.get(url)
        
        # specific wait for this page
        wait = WebDriverWait(driver, 15)

        try:
            # Look for the wake-up button
            # Note: The text might vary slightly, but 'Yes, get this app back up' is standard.
            button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Yes, get this app back up')]"))
            )
            print("  -> Wake-up button found. Clicking...")
            button.click()

            # After clicking, check if it disappears (confirmation action was registered)
            try:
                wait.until(EC.invisibility_of_element_located((By.XPATH, "//button[contains(text(),'Yes, get this app back up')]")))
                print("  -> Button clicked and disappeared ✅ (app should be waking up)")
            except TimeoutException:
                print("  -> Button was clicked but did NOT disappear ⚠️ (might need manual check)")

        except TimeoutException:
            # No button at all → app is assumed to be awake
            print("  -> No wake-up button found. Assuming app is already awake ✅")

    except Exception as e:
        print(f"  -> Error processing {url}: {e}")

def main():
    urls = get_urls()
    
    if not urls:
        print("No URLs found to check.")
        return

    print(f"Found {len(urls)} apps to process.")

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    # Initialize driver once
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        exit(1)

    try:
        for url in urls:
            wake_up_app(driver, url)
            # Optional: small pause between requests to prevent rate limiting
            time.sleep(2) 
            
    finally:
        if driver:
            driver.quit()
        print("--------------------------------------------------")
        print("Script finished.")

if __name__ == "__main__":
    main()