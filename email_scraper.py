import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import urljoin, urlparse

# Configuration
CSV_PATH = "hamburg_results.csv"  # Change this to your CSV file path
TIMEOUT = 10  # Timeout in seconds for page loads

# Keywords for finding contact/about pages (English and German)
CONTACT_KEYWORDS = [
    'kontakt', 'contact', 'impressum', 'about', 'über uns', 
    'ueber uns', 'about us', 'contact us', 'kontaktieren'
]

# Email regex pattern
EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

def setup_driver():
    """Initialize Chrome WebDriver with options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(TIMEOUT)
    return driver

def extract_emails_from_text(text):
    """Extract all email addresses from text"""
    emails = re.findall(EMAIL_PATTERN, text)
    # Filter out common false positives
    filtered_emails = [
        email for email in emails 
        if not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))
    ]
    return list(set(filtered_emails))  # Remove duplicates

def find_contact_links(driver, base_url):
    """Find links that might lead to contact/about pages"""
    contact_links = []
    try:
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            try:
                href = link.get_attribute('href')
                text = link.text.lower()
                
                if href and any(keyword in text or keyword in href.lower() for keyword in CONTACT_KEYWORDS):
                    full_url = urljoin(base_url, href)
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        contact_links.append(full_url)
            except:
                continue
    except:
        pass
    
    return list(set(contact_links))[:5]  # Limit to 5 most relevant links

def extract_email_from_website(driver, url):
    """Extract email from a website by checking homepage and contact pages"""
    emails = []
    visited_urls = set()
    
    try:
        # Visit main page
        print(f"  Visiting: {url}")
        driver.get(url)
        time.sleep(2)  # Wait for page to load
        
        # Extract emails from homepage
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        emails.extend(extract_emails_from_text(page_text))
        
        if emails:
            print(f"  ✓ Found email(s) on homepage: {emails[0]}")
            return emails[0]
        
        visited_urls.add(url)
        
        # Find and visit contact pages
        contact_links = find_contact_links(driver, url)
        print(f"  Found {len(contact_links)} potential contact page(s)")
        
        for contact_url in contact_links:
            if contact_url in visited_urls:
                continue
                
            try:
                print(f"  Visiting contact page: {contact_url}")
                driver.get(contact_url)
                time.sleep(2)
                
                page_text = driver.find_element(By.TAG_NAME, 'body').text
                emails.extend(extract_emails_from_text(page_text))
                
                if emails:
                    print(f"  ✓ Found email(s) on contact page: {emails[0]}")
                    return emails[0]
                
                visited_urls.add(contact_url)
            except Exception as e:
                print(f"  Error visiting {contact_url}: {str(e)}")
                continue
        
        print("  ✗ No email found")
        return ""
        
    except TimeoutException:
        print(f"  ✗ Timeout loading {url}")
        return ""
    except WebDriverException as e:
        print(f"  ✗ Error loading {url}: {str(e)}")
        return ""
    except Exception as e:
        print(f"  ✗ Unexpected error: {str(e)}")
        return ""

def process_csv(csv_path):
    """Process CSV file and extract emails from websites"""
    # Read CSV
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # Auto-detects delimiter (comma by default)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Add email column if it doesn't exist
    if 'email' not in fieldnames:
        fieldnames = list(fieldnames) + ['email']
    
    # Setup Selenium driver
    print("Setting up Chrome WebDriver...")
    driver = setup_driver()
    
    try:
        # Process each row
        for i, row in enumerate(rows, 1):
            website = row.get('website', '').strip()
            
            if not website:
                print(f"\n[{i}/{len(rows)}] No website provided, skipping...")
                row['email'] = ""
                continue
            
            print(f"\n[{i}/{len(rows)}] Processing: {website}")
            
            # Extract email
            email = extract_email_from_website(driver, website)
            row['email'] = email
            
            # Small delay between requests
            time.sleep(1)
    
    finally:
        driver.quit()
        print("\n\nBrowser closed.")
    
    # Write results back to CSV
    output_path = csv_path.replace('.csv', '_with_emails.csv')
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)  # Uses comma by default
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Results saved to: {output_path}")
    
    # Print summary
    emails_found = sum(1 for row in rows if row.get('email'))
    print(f"\nSummary:")
    print(f"  Total websites: {len(rows)}")
    print(f"  Emails found: {emails_found}")
    print(f"  Emails not found: {len(rows) - emails_found}")

if __name__ == "__main__":
    print("=" * 60)
    print("Website Email Extractor")
    print("=" * 60)
    
    try:
        process_csv(CSV_PATH)
    except FileNotFoundError:
        print(f"\n✗ Error: CSV file not found at '{CSV_PATH}'")
        print("  Please update the CSV_PATH variable with the correct path.")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)