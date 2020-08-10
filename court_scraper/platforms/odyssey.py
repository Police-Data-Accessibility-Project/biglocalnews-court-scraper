import shutil
import re
import time
from pathlib import Path

from my_fake_useragent import UserAgent
from retrying import retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


from selenium.webdriver.common.by import By


## Locators
class LoginPageLocators:

    USERNAME = (By.ID, 'UserName')
    PASSWORD = (By.ID, 'Password')
    SIGN_IN_BUTTON = (By.CSS_SELECTOR, '.btn.btn-primary')


class PortalPageLocators:

    PORTAL_BUTTONS = (By.CSS_SELECTOR, '.portlet-buttons')
    IMAGES = (By.TAG_NAME, 'img')


class SearchPageLocators:

    GO_BUTTON = (By.ID, 'submit')
    SEARCH_BOX = (By.CSS_SELECTOR, '#SearchCriteriaContainer input')
    SEARCH_SUBMIT_BUTTON = (By.XPATH, '//*[@id="btnSSSubmit"]')


class SearchResultsPageLocators:

    RESULTS_DIV = (By.CSS_SELECTOR, '#SmartSearchResults')
    NO_RESULTS_MSG = (By.XPATH, '//*[@id="ui-tabs-1"]/div/p')
    CASE_DETAIL_LINK = (By.CSS_SELECTOR, 'a.caseLink')
    # Get table rows that are the grandparent of case links;
    # they contain all case metadata in search results.
    RESULT_ROWS = (By.XPATH, "//a[@class='caseLink']/../..")
    # After a successful search, the page listing all cases
    # can be accessed as the second "step" in a 3-part series
    # of tabs. When a case link is clicked, that changes
    # screen to the 3rd step. To return to the case results list,
    # you must use the below selector and click the link
    CASE_RESULTS_TAB = (
        By.XPATH,
        "//p[@class='step-label' and contains(text(), 'Search Results')]/.."
    )


# Page elements
class SearchBox:

    # locator for search box where search
    # term is entered
    locator = SearchPageLocators.SEARCH_BOX

    def __set__(self, obj, value):
        """Sets the text to the value supplied"""
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(*self.locator)
        )
        driver.find_element(*self.locator).clear()
        driver.find_element(*self.locator).send_keys(value)

    def __get__(self, obj, owner):
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element(*self.locator)
        )
        element = driver.find_element(*self.locator)
        return element.get_attribute("value")


class ResultRow:

    def __init__(self, row_element):
        self.el = row_element

    @property
    def metadata(self):
        case_detail_url = self.el.find_element(
                *SearchResultsPageLocators.CASE_DETAIL_LINK
            ).get_attribute('data-url')
        case_num, style_def, file_date, status, party_name = [
            field.strip() for field in self.inner_text.split('\t')
        ]
        return {
            'case_num': case_num,
            'style_defendant': style_def,
            'file_date': file_date,
            'status': status,
            'party_name': party_name,
            'case_detail_url': case_detail_url,
        }

    @property
    def is_case_row(self):
        case_num = self.inner_text.split('\t')[0]
        case_num_pattern = r'^\d\d[A-Z0-9]{6}$'
        if re.match(case_num_pattern, case_num) and len(case_num) == 8:
            return True
        return False

    @property
    def inner_text(self):
        return self.el.get_attribute('innerText').strip('\t')

    @property
    def detail_page_link(self):
        return self.el.find_element(
            *SearchResultsPageLocators.CASE_DETAIL_LINK
        )

class CaseDetailLinks:

    locator = SearchResultsPageLocators.CASE_DETAIL_LINK

    def __get__(self, obj, owner):
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_elements(*self.locator)
        )
        return driver.find_elements(*self.locator)

class SearchResults:

    locator = SearchResultsPageLocators.RESULT_ROWS

    def __get__(self, obj, owner):
        """Gets the text of the specified object"""
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_elements(*self.locator)
        )
        elements = driver.find_elements(*self.locator)
        case_rows = self._prep_case_rows(elements)
        return case_rows

    def _prep_case_rows(self, elements):
        case_rows = []
        for el in elements:
            row = ResultRow(el)
            if row.is_case_row:
                case_rows.append(row)
        return case_rows

## Pages
class BasePage:

    def __init__(self, driver):
        self.driver = driver

    def fill_form_field(self, locator_name, value):
        element = self._get_element_by_locator(locator_name)
        element.send_keys(value)

    def click(self, locator_name):
        element = self._get_element_by_locator(locator_name)
        element.click()

    def _get_element_by_locator(self, locator_name):
        locator = getattr(self.locators, locator_name)
        return self.driver.find_element(*locator)


# TODO: Refactor to use FormFieldElement or UsernameField
# and PasswordField (sted of fill_form_field), to
# match the page element strategy used for SearchBox field
# on SearchPage
class LoginPage(BasePage):

    locators = LoginPageLocators

    def __init__(self, driver, url, username, password):
        super().__init__(driver)
        self.username = username
        self.password = password
        self.site_url = url
        base_url = self.site_url.split('Home')[0].rstrip('/')
        self.login_url = base_url + '/Account/Login'

    def go_to(self):
        self.driver.get(self.login_url)

    def login(self):
        self.fill_form_field('USERNAME', self.username)
        self.fill_form_field('PASSWORD', self.password)
        self.click('SIGN_IN_BUTTON')


class PortalPage(BasePage):

    locators = PortalPageLocators

    def go_to_hearings_search(self):
        self._click_port_button('hearings')

    def go_to_smart_search(self):
        self._click_port_button('smart_search')

    def _click_port_button(self, name):
        images = self.driver.find_elements(*PortalPageLocators.IMAGES)
        img_names = {
            'hearings' : 'Icon_SearchHearing.svg',
            'smart_search': 'Icon_SmartSearch.svg'
        }
        image_name = img_names['smart_search']
        button = None
        for img in images:
            src = img.get_attribute('src')
            if src.endswith(image_name):
                # If image matches, get parent anchor tag
                button = img.find_element_by_xpath('..')
                break
        button.click()


class SearchPage(BasePage):

    search_box = SearchBox()

    def submit_search(self, timeout=30):
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                SearchPageLocators.SEARCH_SUBMIT_BUTTON
            )
        )
        self.driver.find_element(
            *SearchPageLocators.SEARCH_SUBMIT_BUTTON
        ).click()


class SearchResultsPage(BasePage):

    results = SearchResults()
    case_detail_links = CaseDetailLinks()

    @retry(
        stop_max_attempt_number=7,
        stop_max_delay=30000,
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000
    )
    def results_found(self):
        try:
            results_el = self.driver.find_element(
                *SearchResultsPageLocators.RESULTS_DIV
            )

            found = True
        except NoSuchElementException:
            pass
        try:
            no_results_el = self.driver.find_element(
                *SearchResultsPageLocators.NO_RESULTS_MSG
            )
        except NoSuchElementException:
            pass
        if results_el and found == True:
            return True
        elif 'No cases match' in no_results.get_attribute('innerText'):
            return False
        else:
            raise Exception("Search not yet completed")

    def back_to_search_results(self):
        self.driver.find_element(
            *SearchResultsPageLocators.CASE_RESULTS_TAB
        ).click()

class OdysseySite:

    def __init__(self, url, username, password, download_dir, timeout=60):
        self.site_url = url
        self.username = username
        self.password = password
        self.download_dir = download_dir
        self.timeout = timeout

    def search(self, search_terms, get_detail_page_html=False, headless=True):
        self.driver = self._init_chrome_driver(headless=headless)
        login_page = LoginPage(
            self.driver,
            self.site_url,
            self.username,
            self.password
        )
        login_page.go_to()
        login_page.login()
        portal_page = PortalPage(self.driver)
        portal_page.go_to_smart_search()
        results = []
        try:
            for term in search_terms:
                # Conduct search
                search_page = SearchPage(self.driver)
                search_page.search_box = term
                search_page.submit_search(self.timeout)
                results_page = SearchResultsPage(self.driver)
                if results_page.results_found():
                    for case_row in results_page.results:
                        row_data = case_row.metadata
                        if get_detail_page_html:
                            # TODO proper wait timer, or possibly
                            # make case row a legit descriptor
                            case_row.detail_page_link.click()
                            time.sleep(2)
                            row_data['page_source'] = self.driver.page_source
                            results_page.back_to_search_results()
                        results.append(row_data)
            return results
        finally:
            self.driver.quit()

    def _init_chrome_driver(self, headless=True):
        chrome_options = self._build_chrome_options(headless=headless)
        executable_path = shutil.which('chromedriver')
        driver = webdriver.Chrome(options=chrome_options, executable_path=executable_path)
        return driver

    def _build_chrome_options(self, headless=True):
        # this code alters the browser to download the pdfs
        # it was taken from https://medium.com/@moungpeter/how-to-automate-downloading-files-using-python-selenium-and-headless-chrome-9014f0cdd196
        def enable_download_headless(browser, download_dir):
            browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
            browser.execute("send_command", params)
        # Options were slightly modified by commenting out things I didn't want
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--verbose')
        chrome_options.add_experimental_option("prefs", {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "safebrowsing.enabled": False
        })
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        ua = UserAgent(family='chrome')
        randomua = ua.random()
        chrome_options.add_argument(f'user-agent={randomua}')
        return chrome_options


