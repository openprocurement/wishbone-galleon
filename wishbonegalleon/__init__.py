"""wishbonegalleon - Wishbone Encode modules to use galleon transforms"""

import yaml
import json

from wishbone.module import ProcessModule
from galleon import Mapper
from jsonschema import RefResolver

from .utils import TAGGERS


class GalleonModule(ProcessModule):

    def __init__(
            self,
            config,
            schema,
            mapping,
            tagger="",
            destination="data"
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
                schema = json.load(_file)
        self.mapper = Mapper(mapping, RefResolver.from_schema(schema))

        if tagger and (tagger in TAGGERS):
            self.tagger = TAGGERS[tagger]
    
    def consume(self, event):
        raw_data = event.dump().get('data', {})
        try:
            if raw_data and not raw_data.get('_id', '').startswith('_'):
                data = self.mapper.apply(raw_data)
                if data:
                    if hasattr(self, 'tagger'):
                        data = self.tagger(data)

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
        
