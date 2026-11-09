import math


def parse_zone(text):
    """Parse 'name:area'. Returns (Name, area) or None if input is invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:                      
        return None
    name, area_str = parts[0].strip(), parts[1].strip()
    if not name:                             
        return None
    try:
        area = float(area_str)
    except ValueError:                       
        return None
    if not math.isfinite(area) or area < 0:  
        return None
    return name.title(), area


def moisture_average(readings_csv):
    """Average of comma-separated moisture readings (0-100). None if invalid."""
    if not isinstance(readings_csv, str):
        return None
    values = []
    for r in readings_csv.split(','):
        try:
            v = int(r.strip())
        except ValueError:                   
            return None
        if not 0 <= v <= 100:                
            return None
        values.append(v)
    if not values:                           
        return None
    return sum(values) // len(values)


def water_needed(text):
    """Parse 'area|rainfall' and return water needed (>= 0). None if invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:                      
        return None
    try:
        plot = float(parts[0].strip())
        rain = float(parts[1].strip())
    except ValueError:
        return None
    if not (math.isfinite(plot) and math.isfinite(rain)):
        return None
    if plot < 0 or rain < 0:
        return None
    need = plot * 5 - rain
    if not math.isfinite(need):              
        return None
    return max(need, 0)


def main():
    print("==== Running parse_zone ====")
    user_input = input("Enter zone:area in m2 (e.g. north:120): ")
    result = parse_zone(user_input)
    print("Zone and Area:", result if result is not None else "Invalid input")

    print("\n==== Running moisture_average ====")
    user_input = input("Enter moisture readings as CSV (e.g. 40,35,50): ")
    result = moisture_average(user_input)
    print("Average Moisture:", result if result is not None else "Invalid input")

    print("\n==== Running water_needed ====")
    user_input = input("Enter area|rainfall (e.g. 120|8): ")
    result = water_needed(user_input)
    print("Water Needed:", result if result is not None else "Invalid input")


if __name__ == "__main__":
    main()