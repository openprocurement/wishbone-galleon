""" wishbonegalleon - Wishbone Encode modules to use galleon transforms """
import ujson
import yaml
from jsonschema import RefResolver
from galleon import Mapper
from wishbone.module import ProcessModule
from .utils import TAGGERS


class GalleonModule(ProcessModule):
    """ Wishbone process module based on galleon transformations """
    def __init__(
            self,
            config,
            schema,
            mapping,
            tagger="",
            with_hash=False,
            destination="data",
    ):
        ProcessModule.__init__(self, config)
        for name in ['inbox', 'outbox']:
            self.pool.createQueue(name)
        self.registerConsumer(self.consume, "inbox")
        if not isinstance(mapping, dict):
            with open(mapping) as _file:
                mapping = yaml.load(_file)
        if not isinstance(schema, dict):
            with open(schema) as _file:
                schema = ujson.load(_file)
        self.mapper = Mapper(mapping, RefResolver.from_schema(schema))
        self.with_hash = with_hash
        if tagger and (tagger in TAGGERS):
            self.tagger = TAGGERS[tagger]

    def consume(self, event):
        """ Consume event, process it and push to output queue """
        raw_data = event.dump().get('data', {})
        try:
            if raw_data and not raw_data.get('_id', '').startswith('_'):
                title = raw_data.get('tiltle', '')
                mode = raw_data.get('mode', '')
                if mode and mode == 'test':
                    self.logging.warn(
                        "Test data. skipping"
                    )
                    return
                if 'test' in title or 'тест' in title.lower():
                    self.logging.warn(
                        "Test data. skipping"
                    )
                    return
                data = self.mapper.apply(raw_data)
                if data:
                    if hasattr(self, 'tagger'):
                        data = self.tagger(data)
                    if self.with_hash:
                        pm_type = data.pop('id')[:3]
                        new_id = hash(ujson.dumps(data))
                        data['id'] = "{}{}".format(pm_type, abs(new_id))

                    event.set(data, event.kwargs.destination)
                    self.submit(event, "outbox")
            else:
                self.logging.info(
                    "Empty data. skipping"
                    )
        except Exception as e:
            self.logging.error(
                "Event {} raised error, skipping. Reason: {}".format(
                    raw_data.get('id', ''), e
                    )
                )
        
