def safe_input(prompt, interrupt_msg=None, allow_empty=True):
    try:
        value = input(prompt).strip()

        if not allow_empty and value == "":
            return None

        return value

    except KeyboardInterrupt:
        print(f"\033[31m{interrupt_msg or 'Input interrupted by user'}\033[0m")
        return None

def build_query_key(search_type, params):
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
