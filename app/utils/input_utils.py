def safe_input(prompt: str, interrupt_msg: str = None, allow_empty: bool = True) -> str | None:
    """
    Safely gets user input from the console.

    The function wraps the built-in input() call to handle KeyboardInterrupt
    and optionally allow or disallow empty input.

    Args:
        prompt (str): The message displayed to the user.
        interrupt_msg (str, optional): Custom message displayed if input is interrupted.
        allow_empty (bool, optional): If False, empty input returns None. Defaults to True.

    Returns:
        str | None: The user input string stripped of leading/trailing whitespace,
        or None if input is interrupted or empty input is not allowed.
    """
    try:
        value = input(prompt).strip()

        if not allow_empty and value == "":
            return None

        return value

    except KeyboardInterrupt:
        print(f"\033[31m{interrupt_msg or 'Input interrupted by user'}\033[0m")
        return None


def build_query_key(search_type: str, params: dict) -> str:
    """
    Builds a unique query key string based on the search type and parameters.

    Args:
        search_type (str): The type of search ('keyword', 'genre', 'years', 'genre_years').
        params (dict): Dictionary containing relevant parameters for the search type.

    Returns:
        str: A formatted string used as a unique query key. Example outputs:
            - 'keyword_rock'
            - 'genre_jazz'
            - 'years_1990_2000'
            - 'genre_years_rock_1990_2000'
          Returns 'unknown_query' if expected keys are missing.

    Raises:
        KeyError: Handled internally; prints an error message and returns 'unknown_query'.
    """
    try:
        if search_type == "keyword":
            return f"{search_type}_{params['keyword']}"
        if search_type == "genre":
            return f"{search_type}_{params['genre']}"
        if search_type == "years":
            return f"{search_type}_{params['start_year']}_{params['end_year']}"
        if search_type == "genre_years":
            return f"{search_type}_{params['genre']}_{params['start_year']}_{params['end_year']}"
    except KeyError as e:
        print(f"UNKNOWN_QUERY: Error in keys: {e}")
        return "unknown_query"
