from pkg_resources import iter_entry_points

TAGGERS = {}


def ocds_tagger(data):
    tags = ['tender']
    for key in ['contract', 'award']:
        field = "{}s".format(key)
        if field  in data and (data.get(field, '')):
            tags.append(key)
    data['tag'] = tags
    return data


for name in iter_entry_points('galleon.taggers'):
    TAGGERS[name.name] = name.load()
