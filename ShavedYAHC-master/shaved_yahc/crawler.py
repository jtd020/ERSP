# vim: set tw=99:

from abc import ABCMeta, abstractmethod
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .store import YAHCStore

class YAHCBaseCrawler(object):
    '''YAHC Base Crawler Class

    User Attributes:
        store_location -- str
            Absolute path to the crawl data store directory.
        page_load_time -- int
            Seconds to wait to allow each page to fully load.
        reset_profile_time -- int
            Maximum seconds to allow for resetting the browser profile after crawling a page.
        headless -- bool
            Whether the browser should run in headless mode.
        save_source -- bool
            Whether the crawler should save the source of each page.
        save_screenshots -- bool
            Whether the crawler should save a screenshot of each page.
        save_cookies -- bool
            Whether the browser should save its cookies for each page.
        save_links: -- bool
            Whether the crawler should save the set of all URLs linked from each page.
        save_js -- bool
            Whether the crawler should save script info for each page.
        save_css -- bool
            Whether the crawler should save style info for each page.

    Other Attributes:
        urls_crawled -- int
            The number of URLs crawled by this crawler instance.
        store -- shaved_yahc.store.YAHCStore
            File system store for crawl data.
        driver -- selenium.webdriver.remote.webdriver.WebDriver
            The WebDriver instance used for crawling.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, store_location,
            page_load_time=10, reset_profile_time=10,
            headless=True, save_source=False, save_screenshots=False, save_cookies=False,
            save_links=False, save_js=False, save_css=False, save_computedstyle=False):
        self.page_load_time = page_load_time
        self.reset_profile_time = reset_profile_time

        self.headless = headless
        self.save_source = save_source
        self.save_screenshots = save_screenshots
        self.save_cookies = save_cookies
        self.save_links = save_links
        self.save_js = save_js
        self.save_css = save_css
        self.save_computedstyle = save_computedstyle

        self.urls_crawled = 0

        self.store_location = store_location
        self.store = YAHCStore(self.store_location)

        self.driver = self._setup()
        try:
            self._clear_state()
        except:
            self.shutdown()
            raise

    @abstractmethod
    def _setup(self):
        '''Perform browser-specific setup.

        Returns -- selenium.webdriver.remote.webdriver.WebDriver
            The WebDriver instance to use for crawling.
        '''
        pass

    @abstractmethod
    def _reset_profile(self):
        '''Reset the browser profile to a "like-new" configuration.'''
        pass

    def __enter__(self):
        return self

    def __exit__(self, ty, value, traceback):
        self.shutdown()

    def shutdown(self):
        self.driver.quit()

    def crawl_url(self, url):
        '''
        Crawl the given URL.

        Generated data will be saved in the data store under an index which increments with each
        URL crawled.

        Parameters:
            url -- str
                The URL to crawl.
        '''

        try:
            crawl_id = self.urls_crawled
            self.urls_crawled += 1

            try:
                self._navigate_and_wait(url, self.page_load_time).until(lambda driver: False)
            except TimeoutException:
                pass

            crawl_store = self.store.add_store(str(crawl_id))
            self._capture_state(crawl_store, url)
        finally:
            self._clear_state()

    def _navigate_and_wait(self, url, timeout):
        self.driver.set_page_load_timeout(timeout)

        start_time = time.time()
        self.driver.get(url)
        end_time = time.time()

        elapsed_time = end_time - start_time
        remaining_time = timeout - elapsed_time
        return WebDriverWait(self.driver, remaining_time)

    def _fetch_url_text(self, url, timeout):
        self.driver.set_page_load_timeout(timeout)
        self.driver.get('view-source:{}'.format(url))
        return self.driver.find_element_by_tag_name('body').text

    def _capture_state(self, crawl_store, original_url):
        state = {}
        state['original_url'] = original_url
        state['current_url'] = self.driver.current_url
        state['title'] = self.driver.title

        if self.save_computedstyle:
            css_info = self.driver.execute_script('''
                    let para = document.getElementsByTagName('a')
                    styles = [];
                    for (let i = para.length - 1; i >= 0; --i) {
                        let property = window.getComputedStyle(para[i]);
                        let color = property.getPropertyValue('color');
                        styles.push(color);
                    }
                    return styles; 
                ''')
            state['computedstyle'] = css_info

        if self.save_source:
            state['source_file'] = 'page.html'
            crawl_store.add_text_blob(state['source_file'], self.driver.page_source)

        if self.save_screenshots:
            state['screenshot_file'] = 'screenshot.png'
            screenshot = self.driver.get_screenshot_as_png()
            crawl_store.add_binary_blob(state['screenshot_file'], screenshot)

        if self.save_cookies:
            state['cookies'] = self.driver.get_cookies()

        if self.save_links:
            link_urls = set()
            link_elements = self.driver.find_elements_by_tag_name('a')

            for link_element in link_elements:
                link_url = link_element.get_attribute('href')
                if link_url:
                    link_urls.add(link_url)

            state['links'] = list(link_urls)

        if self.save_js:
            scripts_list = []
            script_elements = self.driver.find_elements_by_tag_name('script')

            for script_element in script_elements:
                script_data = {}

                script_url = script_element.get_attribute('src')
                if script_url:
                    script_data['url'] = script_url

                script_src = script_element.get_property('textContent').strip()
                if script_src:
                    script_data['src'] = script_src

                scripts_list.append(script_data)

            state['js'] = scripts_list

        if self.save_css:
            css_info = self.driver.execute_script('''
                const summaries = [];
                const urls = new Set();

                for (const sheet of document.styleSheets) {
                    let src = '';
                    try {
                        for (const rule of sheet.cssRules) {
                            if (src !== '') {
                                src += '\\n';
                            }
                            src += rule.cssText;
                        }
                    } catch (e) {
                        if (sheet.href) {
                            // Cross-origin stylesheets will cause a SecurityException
                            // to be thrown when we try to retrieve their cssRules.
                            // Note down their URLs for later fetching.
                            urls.add(sheet.href);
                            continue;
                        } else {
                            throw e;
                        }
                    }

                    const summary = { src };
                    if (sheet.href) {
                        summary.url = sheet.href;
                    }

                    summaries.push(summary);
                }

                return { summaries, urls: Array.from(urls) };
            ''')

            summaries = css_info['summaries']
            for url in css_info['urls']:
                try:
                    src = self._fetch_url_text(url, self.page_load_time)
                except (TimeoutException, WebDriverException):
                    continue

                summaries.append({
                    'src': src,
                    'url': url
                })

            state['css'] = summaries

        state_blob = crawl_store.add_json_blob('state.json', state)


    def _clear_state(self):
        self.driver.fullscreen_window()
        self._reset_profile()
        self.driver.get('about:blank')
        self.driver.fullscreen_window()

class YAHCFirefoxCrawler(YAHCBaseCrawler):
    '''YAHC Firefox Crawler Class'''

    def _setup(self):
        options = webdriver.firefox.options.Options()

        if self.headless:
            options.add_argument('--headless')

        # Used for fetching URL content through the browser
        options.set_preference('view_source.syntax_highlight', False)

        return webdriver.Firefox(firefox_options=options)

    def _reset_profile(self):
        wait = self._navigate_and_wait('about:preferences#privacy', self.reset_profile_time)

        wait.until(EC.element_to_be_clickable((By.ID, 'clearHistoryButton'))).click()

        wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.dialogFrame[name=dialogFrame-0]')))

        self.driver.execute_script('''
            const dialog = document.querySelector('.dialogFrame[name=dialogFrame-0]')
                .contentDocument.documentElement;

            // Set "Time range to clear" to "Everything"
            const durationDropdown = dialog.querySelector('#sanitizeDurationChoice');
            durationDropdown.selectedIndex = durationDropdown.itemCount - 1;

            // Select all the types of data that can be cleared
            const categoryCheckboxes = dialog.getElementsByTagName('checkbox');
            for (const categoryCheckbox of categoryCheckboxes) {
                categoryCheckbox.checked = true;
            }

            dialog.acceptDialog();
        ''')

class YAHCChromeCrawler(YAHCBaseCrawler):

    def _setup(self):
        options = webdriver.chrome.options.Options()

        if self.headless:
                options.add_argument('--headless')

        #options.set_preference('view_source.syntax_highlight', False)

        return webdriver.Chrome(chrome_options=options)


    def get_clear_browsing_button(driver):
        return driver.find_element_by_css_selector('* /deep/ #clearBrowserDataConfirm')


    def _reset_profile(self):
        wait = self._navigate_and_wait('chrome://settings/clearBrowserData', self.reset_profile_time)

        wait.until(get_clear_browsing_button)

        get_clear_browsing_button(self.driver).click()

        wait.until_not(get_clear_browsing_button)

