def get_season(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5, 6]:
        return "spring"
    elif month in [7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
