# Configuration file for Google Maps Scraper

# Cities to scrape
CITIES = [
    'Berlin',
    'Leipzig',
    'Hamburg'
    # Add more cities here
    # 'Munich',
    # 'Cologne',
    # 'Frankfurt',
    # 'Dresden'
]

# Search queries/categories
SEARCH_QUERIES = [
    'restaurant',
    'cafe',
    'food',
    'bistro',
    'imbiss',
    # Add more categories
    # 'pizzeria',
    # 'sushi restaurant',
    # 'burger restaurant',
    # 'bakery',
    # 'ice cream shop'
]

# Scraping settings
MAX_RESULTS_PER_QUERY = 20  # Maximum number of results to scrape per query
MAX_SCROLLS = 5  # Maximum number of scrolls in results list
HEADLESS_MODE = False  # Set to True to run without browser window

# Delay settings (in seconds)
MIN_DELAY = 2  # Minimum delay between actions
MAX_DELAY = 5  # Maximum delay between actions
CITY_BREAK_MIN = 30  # Minimum break between cities
CITY_BREAK_MAX = 60  # Maximum break between cities

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
]

# Output settings
OUTPUT_DIR = 'output'  # Directory for output files
SAVE_CSV = True  # Save as CSV
SAVE_EXCEL = True  # Save as Excel
SAVE_JSON = False  # Save as JSON

# Logging settings
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'scraper.log'