import time
import random
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import re
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class ProxyManager:
    """Manages proxy rotation for anonymity"""
    
    def __init__(self):
        self.current_proxy = None
        self.proxy_list = []
        
    def get_free_proxies(self):
        """Fetch free proxies from multiple sources"""
        proxies = []
        
        try:
            # Source 1: Free Proxy List
            response = requests.get('https://www.proxy-list.download/api/v1/get?type=http', timeout=10)
            if response.status_code == 200:
                proxy_list = response.text.split('\r\n')
                proxies.extend([p for p in proxy_list if p])
        except Exception as e:
            logging.warning(f"Failed to fetch proxies from source 1: {e}")
        
        try:
            # Source 2: Proxy Scrape
            response = requests.get('https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all', timeout=10)
            if response.status_code == 200:
                proxy_list = response.text.split('\r\n')
                proxies.extend([p for p in proxy_list if p])
        except Exception as e:
            logging.warning(f"Failed to fetch proxies from source 2: {e}")
        
        # Remove duplicates
        self.proxy_list = list(set(proxies))
        logging.info(f"Loaded {len(self.proxy_list)} proxies")
        
        return self.proxy_list
    
    def test_proxy(self, proxy):
        """Test if a proxy is working"""
        try:
            test_url = 'https://httpbin.org/ip'
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get(test_url, proxies=proxies, timeout=5)
            if response.status_code == 200:
                logging.info(f"✓ Proxy {proxy} is working. IP: {response.json().get('origin')}")
                return True
        except:
            return False
        return False
    
    def get_working_proxy(self, max_tries=10):
        """Get a working proxy from the list"""
        if not self.proxy_list:
            self.get_free_proxies()
        
        for _ in range(max_tries):
            if not self.proxy_list:
                break
                
            proxy = random.choice(self.proxy_list)
            if self.test_proxy(proxy):
                self.current_proxy = proxy
                return proxy
            else:
                self.proxy_list.remove(proxy)
        
        logging.warning("No working proxy found")
        return None


class GoogleMapsScraper:
    def __init__(self, headless=False, use_proxy=True):
        """Initialize the scraper with Chrome options and proxy support"""
        self.options = Options()
        self.use_proxy = use_proxy
        self.proxy_manager = ProxyManager() if use_proxy else None
        
        # Make the browser appear more natural
        if headless:
            self.options.add_argument('--headless')
        
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Disable WebRTC to prevent IP leaks
        self.options.add_argument('--disable-webrtc')
        self.options.add_argument('--disable-webrtc-multiple-routes')
        self.options.add_argument('--disable-webrtc-hw-encoding')
        self.options.add_argument('--disable-webrtc-hw-decoding')
        self.options.add_argument('--enforce-webrtc-ip-permission-check')
        
        # Additional privacy settings
        self.options.add_argument('--disable-geolocation')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-media-stream')
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        self.options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        # Setup proxy if enabled
        if self.use_proxy:
            proxy = self.proxy_manager.get_working_proxy()
            if proxy:
                self.options.add_argument(f'--proxy-server={proxy}')
                logging.info(f"Using proxy: {proxy}")
            else:
                logging.warning("No proxy available, continuing without proxy")
                self.use_proxy = False
        
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Additional WebDriver fingerprint masking
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.options.arguments[self.options.arguments.index([arg for arg in self.options.arguments if 'user-agent' in arg][0])].split('=')[1]
        })
        
        # Mask WebRTC IP leak
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        self.wait = WebDriverWait(self.driver, 10)
        
    def check_ip(self):
        """Check current IP address"""
        try:
            self.driver.get('https://httpbin.org/ip')
            self.natural_delay(2, 3)
            ip_info = self.driver.find_element(By.TAG_NAME, 'pre').text
            logging.info(f"Current IP info: {ip_info}")
            return ip_info
        except Exception as e:
            logging.error(f"Could not check IP: {e}")
            return None
    
    def rotate_proxy(self):
        """Switch to a new proxy"""
        if not self.use_proxy or not self.proxy_manager:
            return False
        
        logging.info("Rotating proxy...")
        self.driver.quit()
        
        proxy = self.proxy_manager.get_working_proxy()
        if proxy:
            self.options.add_argument(f'--proxy-server={proxy}')
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            logging.info(f"Switched to new proxy: {proxy}")
            return True
        
        logging.warning("Could not rotate proxy")
        return False
        
    def natural_delay(self, min_seconds=2, max_seconds=5):
        """Add random delay to mimic human behavior"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def scroll_element(self, element, scrolls=3):
        """Scroll within an element naturally"""
        for i in range(scrolls):
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', element)
            self.natural_delay(1, 2)
    
    def extract_email(self, text):
        """Extract email from text"""
        if not text:
            return None
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_website(self, text):
        """Extract website URL from text"""
        if not text:
            return None
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls[0] if urls else None
    
    def search_location(self, city, query):
        """Search for establishments in a specific city"""
        search_query = f"{query} in {city}, Germany"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        logging.info(f"Searching: {search_query}")
        self.driver.get(url)
        self.natural_delay(3, 5)
        
    def get_results_container(self):
        """Get the scrollable results container"""
        try:
            # Wait for results to load
            results = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            return results
        except TimeoutException:
            logging.warning("Could not find results container")
            return None
    
    def scroll_results(self, container, max_scrolls=10):
        """Scroll through results to load more establishments"""
        logging.info("Scrolling through results...")
        
        for i in range(max_scrolls):
            # Get current scroll height
            last_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", container
            )
            
            # Scroll down
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", container
            )
            self.natural_delay(2, 4)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", container
            )
            
            # Check if we've reached the end
            if new_height == last_height:
                logging.info("Reached end of results")
                break
                
            logging.info(f"Scroll {i+1}/{max_scrolls} completed")
    
    def extract_place_data(self, place_element):
        """Extract data from a single place listing"""
        data = {
            'name': None,
            'address': None,
            'phone': None,
            'website': None,
            'email': None,
            'rating': None,
            'reviews_count': None
        }
        
        try:
            # Click on the place to open details
            place_element.click()
            self.natural_delay(2, 4)
            
            # Extract name
            try:
                name_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
                )
                data['name'] = name_element.text
            except:
                pass
            
            # Extract address
            try:
                address_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id='address']"
                )
                data['address'] = address_button.get_attribute('aria-label').replace('Address: ', '')
            except:
                pass
            
            # Extract phone
            try:
                phone_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id^='phone:tel:']"
                )
                data['phone'] = phone_button.get_attribute('aria-label').replace('Phone: ', '')
            except:
                pass
            
            # Extract website
            try:
                website_link = self.driver.find_element(
                    By.CSS_SELECTOR, "a[data-item-id='authority']"
                )
                data['website'] = website_link.get_attribute('href')
            except:
                pass
            
            # Extract rating and reviews
            try:
                rating_element = self.driver.find_element(
                    By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']"
                )
                data['rating'] = rating_element.text
                
                reviews_element = self.driver.find_element(
                    By.CSS_SELECTOR, "div.F7nice span[aria-label*='reviews']"
                )
                reviews_text = reviews_element.get_attribute('aria-label')
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    data['reviews_count'] = reviews_match.group(1)
            except:
                pass
            
            # Try to find email in the page content
            try:
                page_text = self.driver.find_element(By.TAG_NAME, 'body').text
                data['email'] = self.extract_email(page_text)
            except:
                pass
            
            logging.info(f"Extracted: {data['name']}")
            
        except Exception as e:
            logging.error(f"Error extracting place data: {str(e)}")
        
        return data
    
    def scrape_city(self, city, queries, max_results=50):
        """Scrape establishments for a given city"""
        all_data = []
        request_count = 0
        
        for query in queries:
            try:
                # Rotate proxy every 30 requests if enabled
                if self.use_proxy and request_count > 0 and request_count % 30 == 0:
                    self.rotate_proxy()
                
                self.search_location(city, query)
                request_count += 1
                
                # Get results container
                container = self.get_results_container()
                if not container:
                    continue
                
                # Scroll to load more results
                self.scroll_results(container, max_scrolls=5)
                
                # Get all place elements
                place_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "div[role='feed'] > div > div > a"
                )
                
                logging.info(f"Found {len(place_elements)} places for '{query}' in {city}")
                
                # Limit results
                places_to_scrape = place_elements[:min(len(place_elements), max_results)]
                
                for idx, place in enumerate(places_to_scrape, 1):
                    try:
                        logging.info(f"Processing {idx}/{len(places_to_scrape)}")
                        
                        data = self.extract_place_data(place)
                        data['city'] = city
                        data['category'] = query
                        data['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        if data['name']:  # Only add if we got at least a name
                            all_data.append(data)
                        
                        self.natural_delay(2, 4)
                        request_count += 1
                        
                    except Exception as e:
                        logging.error(f"Error processing place {idx}: {str(e)}")
                        continue
                
            except Exception as e:
                logging.error(f"Error scraping {query} in {city}: {str(e)}")
                continue
        
        return all_data
    
    def save_to_csv(self, data, filename):
        """Save data to CSV file"""
        if not data:
            logging.warning("No data to save")
            return
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logging.info(f"Saved {len(data)} records to {filename}")
    
    def save_to_excel(self, data, filename):
        """Save data to Excel file"""
        if not data:
            logging.warning("No data to save")
            return
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, engine='openpyxl')
        logging.info(f"Saved {len(data)} records to {filename}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    # Configuration
    cities = ['Hamburg']
    queries = [
        'restaurant',
        'cafe',
        'food',
        'bistro',
        'imbiss'
    ]
    
    # Set use_proxy=True to enable proxy rotation
    # Set use_proxy=False to scrape without proxy
    scraper = GoogleMapsScraper(headless=False, use_proxy=True)
    
    try:
        # Check IP address
        logging.info("\n=== Checking IP Address ===")
        scraper.check_ip()
        
        all_results = []
        
        for city in cities:
            logging.info(f"\n{'='*50}")
            logging.info(f"Starting scraping for {city}")
            logging.info(f"{'='*50}\n")
            
            city_data = scraper.scrape_city(city, queries, max_results=20)
            all_results.extend(city_data)
            
            # Save intermediate results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            scraper.save_to_csv(city_data, f'{city.lower()}_results_{timestamp}.csv')
            
            # Longer delay between cities
            logging.info(f"Completed {city}. Taking a break...")
            time.sleep(random.uniform(30, 60))
        
        # Save final combined results
        final_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scraper.save_to_csv(all_results, f'all_results_{final_timestamp}.csv')
        scraper.save_to_excel(all_results, f'all_results_{final_timestamp}.xlsx')
        
        logging.info(f"\n{'='*50}")
        logging.info(f"Scraping completed! Total records: {len(all_results)}")
        logging.info(f"{'='*50}")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()