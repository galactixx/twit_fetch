import time

from playwright.sync_api import (
    sync_playwright, 
    TimeoutError
)

class PlaywrightBrowser:
    """Playwright browsing interface with helper methods."""
    def __init__(
        self,
        headless: bool = False,
        delay: float = 0.5,
        timeout: int = 10000):
        self._delay = delay
        self._timeout = timeout
        self._browser = (
            sync_playwright().start()
            .chromium.launch(headless=headless))

        self._page = self._browser.new_page()

    def _wait_for_load(self) -> None:
        try:
            self._page.wait_for_load_state("networkidle", timeout=self._timeout)
            self._page.wait_for_function("document.readyState === 'complete'")
            time.sleep(self._delay)
        except TimeoutError:
            pass

    def scroll_down(self) -> None:
        self._page.evaluate("window.scrollBy(0, 1000)")
        self._page.wait_for_timeout(2000)

    def click_on_selection(self, selector: str) -> None:
        self._page.click(selector)
        self._wait_for_load()

    def type_input(self, text: str, selector: str) -> None:
        self._page.type(selector, text)
        self._page.keyboard.press('Enter')
        self._wait_for_load()

    def go_to_page(self, url: str) -> None:
        self._page.goto(url, wait_until='load', timeout=20000)
        self._wait_for_load()

    def go_back_page(self) -> None:
        self._page.go_back()
        self._page.wait_for_timeout(2000)

    def exit_browser(self) -> None:
        self._browser.close()

    def page_to_dom(self) -> str:
        content = self._page.content()
        return content