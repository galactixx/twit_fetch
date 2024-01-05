import time

from playwright.sync_api import (
    Page,
    sync_playwright, 
    TimeoutError
)

from twitfetch._constants import TWEET_ARTICLE

class PlaywrightBrowser:
    """
    Playwright browsing interface with helper methods.
    """
    def __init__(
        self,
        headless: bool = False,
        delay: float = 0.5,
        timeout: int = 10000
    ):
        self._delay = delay
        self._timeout = timeout
        self.browser = (
            sync_playwright().start()
            .chromium.launch(headless=headless)
        )

        self.page: Page = self.browser.new_page()

    def refresh(self) -> None:
        """
        Refresh page.
        """

        self.page.reload()
        self._wait_for_load()

    def _wait_for_load(self) -> None:
        """
        Function used to wait some time until DOM is loaded. 
        """

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=self._timeout)
            self.page.wait_for_function("document.readyState === 'complete'")
            time.sleep(self._delay)
        except TimeoutError:
            pass

    def scroll_down(self, to_bottom: bool = False) -> None:
        """
        Scroll down webpage either slightly or all the way down.
        """

        if to_bottom:
            action = 'window.scrollTo(0, document.body.scrollHeight)'
        else:
            action = 'window.scrollBy(0, 1000)'

        self.page.evaluate(action)
        self.page.wait_for_timeout(2000)

    def click_on_selection(self, selector: str) -> None:
        """
        Click on a button.
        """

        self.page.click(selector)
        self._wait_for_load()

    def type_input(self, text: str, selector: str) -> None:
        """
        Type in an input and hit the enter button.
        """

        self.page.type(selector, text)
        self.page.keyboard.press('Enter')
        self._wait_for_load()

    def go_to_page(self, url: str, wait_for_tweet: bool = False) -> None:
        """
        Navigate to a webpage.
        """

        self.page.goto(url, wait_until='load', timeout=20000)

        if wait_for_tweet:
            self.page.wait_for_selector(
                f'{TWEET_ARTICLE.tag}[{TWEET_ARTICLE.attribute}="{TWEET_ARTICLE.attribute_value}"]',
                timeout=self._timeout
            )
        else:
            self._wait_for_load()

    def go_back_page(self) -> None:
        """
        Go back to the previous webpage.
        """

        self.page.go_back()
        self.page.wait_for_timeout(2000)

    def exit_browser(self) -> None:
        """
        Close the browser instance.
        """

        self.browser.close()

    def page_to_dom(self) -> str:
        """
        Convert the webpage to DOM.
        """

        content = self.page.content()
        return content