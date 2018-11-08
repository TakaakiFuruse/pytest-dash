from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import By


def wait_for_element_by_css_selector(driver, selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def wait_for_text_to_equal(driver, selector, text, timeout=10):
    """

    :param driver:
    :type driver: selenium.webdriver.remote.webdriver.WebDriver
    :param selector:
    :param text:
    :param timeout:
    :return:
    """
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), text)
    )
    assert text == driver.find_element_by_css_selector(selector).text
