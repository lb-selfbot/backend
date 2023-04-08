"""
Generate random credit card numbers
"""
import random

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

        return "".join(map(str, credit_card_number))

    def random_int(self, num1, num2, length):
        """
        Generate a random integer with a specific length
        """
        num = random.randint(num1, num2)
        while len(str(num)) < length:
            num = f"0{num}"
        return num

    def credit_card_number(self, prefix_list, length):
        """
        Generate a credit card number with a specific prefix and length
        """
        prefix = self.generator.choice(prefix_list)
        return {
            "number": self.completed_number(prefix, length),
            "ccv": str(self.random_int(100, 999, 3)),
            "expiry_date": f"{self.random_int(1, 12, 2)}/{self.random_int(23, 30, 2)}",
        }
