import ujson
import yaml
import requests
from pkg_resources import iter_entry_points


PROCESSORS = {}

def load_datafile(path):
    if path.startswith('http'):
        return requests.get(path).json()
    if path.endswith('json'):
        loader = ujson.load
    elif path.endswith('yaml') or path.endswith('yml'):
        loader = yaml.load
    else:
        raise Exception("invalid file extension")
    with open(path) as fd:
        return loader(fd)


def ocds_tagger(instance, data):
    tags = []
    for key in ['contract', 'award']:
        field = "{}s".format(key)
        if field  in data and (data.get(field, '')):
            tags.append(key)
    if 'tender' in data:
        tags.append('tender')
    data['tag'] = tags
    instance.logging.debug('Tagged doc {} as {}'.format(data.get('id'), tags))
    return data


def hashid(instance, data):
    old_id = data.pop('id', '')
    data['id'] = str(abs(hash(ujson.dumps(data))))
    instance.logging.debug("Update doc id {} -> {}".format(
        old_id, data['id']
    ))
    return data


for name in iter_entry_points('wishbonegalleon.processors'):
    PROCESSORS[name.name] = name.load()
