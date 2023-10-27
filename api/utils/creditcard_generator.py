"""
Generate random credit card numbers
"""
import random
import tempfile
import os
from urllib.parse import quote

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from lightningbot import settings

ChromeDriverManager().install()

visa_prefix_list = [
    [4, 5, 3, 9],
    [4, 5, 5, 6],
    [4, 9, 1, 6],
    [4, 5, 3, 2],
    [4, 9, 2, 9],
    [4, 0, 2, 4, 0, 0, 7, 1],
    [4, 4, 8, 6],
    [4, 7, 1, 6],
    [4],
]
mastercard_prefix_list = [[5, 1], [5, 2], [5, 3], [5, 4], [5, 5]]
amex_prefix_list = [[3, 4], [3, 7]]
discover_prefix_list = [[6, 0, 1, 1]]
diners_prefix_list = [
    [3, 0, 0],
    [3, 0, 1],
    [3, 0, 2],
    [3, 0, 3],
    [3, 6],
    [3, 8],
]
enroute_prefix_list = [[2, 0, 1, 4], [2, 1, 4, 9]]
jcb_prefix_list = [[3, 5]]
voyager_prefix_list = [[8, 6, 9, 9]]


def _take_screenshot(url: str) -> bytes:
    # Create a new instance of the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--force-device-scale-factor=3")

    driver = webdriver.Chrome(options)
    driver.set_window_rect(0, 0, 450, 300)

    # Take a screenshot of the page
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()

    driver.quit()

    return screenshot


def create_visualisation(name: str, number: int, exp: str, cvv: str, type: str) -> str:
    with open("templates/creditcard/page.html", "r") as f:
        page = f.read()
    
    name = name.replace("<", "&lt;")

    page = page.replace("{{name}}", name)
    page = page.replace("{{number}}", number)
    page = page.replace("{{exp}}", exp)
    page = page.replace("{{cvv}}", cvv)

    brand_logo = ""
    match type:
        case "mastercard":
            brand_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Mastercard_2019_logo.svg/1200px-Mastercard_2019_logo.svg.png"
        case "visa":
            brand_logo = (
                "https://seeklogo.com/images/V/VISA-logo-DD37676279-seeklogo.com.png"
            )
        case "amex":
            brand_logo = "https://i.pinimg.com/originals/c9/10/94/c910944ac6247ed2d0d47279453c5959.jpg"
        case "discover":
            brand_logo = (
                "https://1000logos.net/wp-content/uploads/2021/05/Discover-logo.png"
            )
        case "diners":
            brand_logo = "https://1000logos.net/wp-content/uploads/2021/05/Diners-Club-International-logo.png"
        case "jcb":
            brand_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/JCB_logo.svg/2560px-JCB_logo.svg.png"

    page = page.replace("{{brand_logo}}", brand_logo)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        f.write(page.encode("utf-8"))
        f.flush()
        url = "file://" + f.name

        screenshot = _take_screenshot(url)

    vis_path = os.path.join(settings.STATIC_ROOT, "creditcards")
    if not os.path.exists(vis_path):
        os.makedirs(vis_path)

    with open(os.path.join(vis_path, f"{number}.png"), "wb") as f:
        f.write(screenshot)

    return f"https://api.lightning-bot.com/static/creditcards/{quote(number)}.png"


class CreditCardGenerator:
    """
    Generate fake valid credit card numbers
    """

    def __init__(self):
        self.generator = random.Random()
        self.generator.seed()

    def luhn_algorithm(self, credit_card_number: str):
        """
        Luhn algorithm to check if a credit card number is valid
        """
        digits = list(map(int, credit_card_number))
        odd_sum = sum(digits[-1::-2])
        even_sum = sum(sum(divmod(2 * d, 10)) for d in digits[-2::-2])
        return (odd_sum + even_sum) % 10

    def completed_number(self, prefix, length):
        """
        Generate a valid credit card number
        """
        credit_card_number = prefix + random.choices(
            range(0, 10), k=length - len(prefix) - 1
        )

        checkdigit = self.luhn_algorithm([*credit_card_number, 0])
        credit_card_number.append(10 - (checkdigit % 10))

        # Add space every 4 digits
        for i in range(4, len(credit_card_number), 5):
            credit_card_number.insert(i, " ")

        return "".join(map(str, credit_card_number))

    def random_int(self, num1, num2, length):
        """
        Generate a random integer with a specific length
        """
        num = random.randint(num1, num2)
        while len(str(num)) < length:
            num = f"0{num}"
        return num

    def credit_card_number(self, prefix_list, length, brand, name="John Doe"):
        """
        Generate a credit card number with a specific prefix and length
        """
        prefix = self.generator.choice(prefix_list)

        number = self.completed_number(prefix, length)
        cvv = str(self.random_int(100, 999, 3))
        exp = f"{self.random_int(1, 12, 2)}/{self.random_int(25, 30, 2)}"

        vis = create_visualisation(name, number, exp, cvv, brand)

        return {
            "number": number,
            "cvv": cvv,
            "expiry_date": exp,
            "visualisation": vis,
        }
