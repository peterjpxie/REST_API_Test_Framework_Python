# *** Change common webdriver settings ***
import pytest
@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    return selenium 

# configure firefox options, i.e. headless   
# https://seleniumhq.github.io/selenium/docs/api/py/webdriver_firefox/selenium.webdriver.firefox.options.html
@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.headless = True
    return firefox_options               
                
# configure Chrome options, i.e. headless 
# https://seleniumhq.github.io/selenium/docs/api/py/webdriver_chrome/selenium.webdriver.chrome.options.html  
@pytest.fixture
def chrome_options(chrome_options):
    # chrome_options.add_argument("--headless")
    return chrome_options
    
    
