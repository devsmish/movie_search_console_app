import datetime


def normalize_year_input(year):
    current_year = datetime.datetime.now().year % 100  # последние 2 цифры

    if isinstance(year, str):
        year = year.strip()
        if len(year) == 2 and year.isdigit():
            year_int = int(year)
        else:
            try:
                return int(year)
            except ValueError:
                raise ValueError("\033[31mIncorrect year!\033[0m")
    else:
        year_int = year

    if year_int <= current_year:
        return 2000 + year_int
    else:
        return 1900 + year_int