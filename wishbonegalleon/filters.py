from pkg_resources import iter_entry_points

FILTERS = {}

def filter_test(instance, data):
    if data and not data.get('_id', '').startswith('_'):
        title = data.get('tiltle', '')
        mode = data.get('mode', '')
        if mode and mode == 'test':
            instance.logging.warn(
                "Test data. skipping"
            )
            return
        if 'test' in title or 'тест' in title.lower():
            instance.logging.warn(
                "Test data. skipping"
            )
            return
    return data


for entry in iter_entry_points('wishbonegalleon.filters'):
    FILTERS[entry.name] = entry.load()
