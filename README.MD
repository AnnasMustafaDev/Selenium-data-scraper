# Google Maps Restaurant Scraper

A Python-based web scraper for extracting restaurant and food establishment data from Google in German cities.

## Features

- 🎯 Scrapes restaurants, cafes, and food establishments
- 🇩🇪 Configured for German cities (Berlin, Leipzig, Hamburg)
- 📊 Exports data to CSV and Excel formats
- 🤖 Natural scraping behavior to avoid detection
- 📝 Detailed logging
- ⏱️ Random delays to mimic human behavior
- 🔄 Automatic scrolling to load more results

## Data Collected

The scraper collects the following information:
- Business name
- Full address
- Phone number
- Website URL
- Email address (if available)
- Rating
- Number of reviews
- City
- Category
- Timestamp of scraping

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed
- ChromeDriver (will be managed automatically)

## Installation

### 1. Clone or download this project

```bash
git clone <your-repo-url>
cd google-maps-scraper
```

### 2. Create a virtual environment

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ChromeDriver

The script uses Selenium with Chrome. Make sure you have Google Chrome installed, then install ChromeDriver:

**Option 1: Automatic (Recommended)**
The script will try to use `webdriver-manager` to handle this automatically.

**Option 2: Manual**
Download ChromeDriver from: https://chromedriver.chromium.org/
- Make sure the version matches your Chrome browser
- Add ChromeDriver to your system PATH

## Usage

### Basic Usage

**With Proxy (Recommended for Privacy):**
```bash
python scraper.py
```

**Without Proxy (Faster but uses your real IP):**
Edit `scraper.py` and change:
```python
scraper = GoogleMapsScraper(headless=False, use_proxy=False)
```

The scraper will:
1. Automatically fetch free proxies from multiple sources
2. Test each proxy to ensure it's working
3. Display your current IP address for verification
4. Rotate proxies every 30 requests
5. Switch to a new proxy if the current one fails

### Configuration

Edit the `main()` function in `scraper.py` to customize:

**Cities:**
```python
cities = ['Berlin', 'Leipzig', 'Hamburg', 'Munich', 'Cologne']
```

**Search Queries:**
```python
queries = [
    'restaurant',
    'cafe',
    'food',
    'bistro',
    'imbiss',
    'pizzeria',
    'sushi'
]
```

**Maximum Results per Query:**
```python
city_data = scraper.scrape_city(city, queries, max_results=20)
```

**Headless Mode (no browser window):**
```python
scraper = GoogleMapsScraper(headless=True, use_proxy=True)
```

**Enable/Disable Proxy:**
```python
# With proxy (anonymous)
scraper = GoogleMapsScraper(headless=False, use_proxy=True)

# Without proxy (faster, but uses your real IP)
scraper = GoogleMapsScraper(headless=False, use_proxy=False)
```

## Output Files

The scraper generates:

1. **Individual city files:** `berlin_results_20250118_143025.csv`
2. **Combined CSV file:** `all_results_20250118_143025.csv`
3. **Combined Excel file:** `all_results_20250118_143025.xlsx`
4. **Log file:** `scraper.log`

## Anti-Detection & Privacy Features

The scraper includes several features to appear more natural and protect your identity:

- ✅ **Automatic Proxy Rotation** - Fetches and rotates free proxies automatically
- ✅ **IP Masking** - Your real IP address is hidden behind proxies
- ✅ **WebRTC Leak Prevention** - Blocks WebRTC to prevent IP leaks
- ✅ **Random User Agents** - Rotates browser fingerprints
- ✅ **Random Delays** - Human-like timing (2-5 seconds between actions)
- ✅ **Human-like Scrolling** - Natural scrolling behavior
- ✅ **Longer Pauses** - 30-60 second breaks between cities
- ✅ **Disabled Automation Flags** - Removes Selenium detection markers
- ✅ **Geolocation Disabled** - Prevents location tracking
- ✅ **Proxy Health Checks** - Tests proxies before use

## Important Notes

### Legal Considerations

⚠️ **Important:** Web scraping may violate Google Maps' Terms of Service. This tool is provided for educational purposes only. Use at your own risk and ensure you comply with:

- Google's Terms of Service
- Local data protection laws (GDPR in Germany)
- Robots.txt directives
- Rate limiting to avoid server overload

### Best Practices

1. **Run during off-peak hours** to reduce load on servers
2. **Use reasonable delays** - don't make requests too quickly
3. **Respect robots.txt** - check if scraping is allowed
4. **Don't scrape excessively** - limit your requests
5. **Consider official APIs** - Google offers a Places API for legitimate use

### Troubleshooting

**Issue: ChromeDriver version mismatch**
```bash
pip install --upgrade webdriver-manager
```

**Issue: Proxy not working**
- The scraper automatically fetches and tests free proxies
- If proxies fail, set `use_proxy=False` to scrape without proxy
- Free proxies can be unreliable - consider using paid proxy services for better reliability
- Premium proxy services: Bright Data, Smartproxy, Oxylabs

**Issue: All proxies failing**
```python
# Run without proxy temporarily
scraper = GoogleMapsScraper(headless=False, use_proxy=False)
```

**Issue: Elements not found**
- Google Maps HTML structure changes frequently
- You may need to update CSS selectors in the code
- Try increasing wait times in the script

**Issue: Getting blocked**
- Enable proxy rotation (`use_proxy=True`)
- Increase delays between requests
- Reduce the number of results per query
- Enable headless mode
- Use premium proxy services

**Issue: Slow scraping with proxies**
- Free proxies are often slower than direct connections
- Consider disabling proxies for faster scraping (but less anonymous)
- Use premium proxy services for better speed

**Issue: No email addresses found**
- Many businesses don't list emails publicly on Google Maps
- Consider visiting the business websites directly
- Some data may require additional clicks/navigation

## Proxy & Anonymity

### Free vs Paid Proxies

**Free Proxies (Built-in):**
- ✅ No cost
- ✅ Automatic rotation
- ✅ Multiple sources
- ❌ Can be slow
- ❌ Less reliable
- ❌ May fail frequently

**Paid Proxies (Recommended for serious use):**
- ✅ Fast and reliable
- ✅ Better success rate
- ✅ Less likely to be blocked
- ✅ Support and guarantees
- ❌ Costs money

### Using Custom/Paid Proxies

To use your own proxy service, modify the `ProxyManager` class:

```python
class ProxyManager:
    def __init__(self):
        # Add your own proxy list here
        self.proxy_list = [
            'proxy1.example.com:8080',
            'proxy2.example.com:8080',
            'proxy3.example.com:8080'
        ]
        # Or use authenticated proxies:
        # 'username:password@proxy.example.com:8080'
```

### Recommended Proxy Services

For production use, consider:
- **Bright Data** (formerly Luminati) - Most reliable
- **Smartproxy** - Good balance of price/performance
- **Oxylabs** - Enterprise-grade
- **ProxyMesh** - Budget-friendly
- **Crawlera** - Specialized for web scraping

## Privacy Notes

### What Gets Hidden:
- Your real IP address (when using proxies)
- Your browser fingerprint (partially)
- Your location data
- WebRTC leaks

### What Doesn't Get Hidden:
- Your account (if you're logged into Google)
- Patterns in scraping behavior
- The fact that you're using Selenium (partially masked)

### Add More Cities

```python
cities = ['Berlin', 'Leipzig', 'Hamburg', 'Dresden', 'Bremen']
```

### Change Scraping Speed

Adjust delays in the `natural_delay()` method:

```python
self.natural_delay(min_seconds=3, max_seconds=7)  # Slower
self.natural_delay(min_seconds=1, max_seconds=2)  # Faster (riskier)
```

### Export to Different Formats

Add custom export methods:

```python
def save_to_json(self, data, filename):
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

## License

This project is provided as-is for educational purposes.

## Disclaimer

This tool is for educational and research purposes only. The developers are not responsible for any misuse or violations of terms of service. Always ensure you have the right to scrape data from any website and comply with all applicable laws and regulations.

## Support

For issues or questions:
1. Check the log file (`scraper.log`) for errors
2. Ensure all dependencies are installed correctly
3. Verify Chrome and ChromeDriver versions match
4. Try running in non-headless mode to see what's happening

---

**Last Updated:** November 2025
