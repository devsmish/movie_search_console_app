import datetime


def normalize_year_input(year: str | int) -> int:
    """
    Normalizes a year input to a four-digit integer.

    Converts 2-digit year inputs to 4-digit format assuming:
    - Years less than or equal to the current year's last two digits are in the 2000s.
    - Years greater than the current year's last two digits are in the 1900s.
    Also accepts full 4-digit year strings or integers.

    Args:
        year (str | int): The input year as a string (2 or 4 digits) or integer.

    Returns:
        int: The normalized year as a 4-digit integer.

    Raises:
        ValueError: If the input cannot be converted to an integer.
    """
    current_year = datetime.datetime.now().year % 100  # last 2 digits

    if isinstance(year, str):
        year = year.strip()
        if len(year) == 2 and year.isdigit():
            year_int = int(year)
        else:
            try:
                return int(year)
            except ValueError:
                raise ValueError("Incorrect year!")
    else:
        year_int = year

    if 0 <= year_int <= current_year:
        return 2000 + year_int
    else:
        return 1900 + year_int
