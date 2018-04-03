from pkg_resources import iter_entry_points

TAGGERS = {}


def ocds_tagger(data):
    tags = ['tender']
    for key in ['contract', 'award']:
        if "{}s".format(key) in data:
            tags.append(key)
    data['tag'] = tags
    return data


for name in iter_entry_points('galleon.taggers'):
    TAGGERS[name.name] = name.load()