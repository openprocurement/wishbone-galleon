"""wishbonegalleon - Wishbone Encode modules to use galleon transforms"""

import yaml
import json

from wishbone.module import ProcessModule
from galleon import Mapper
from jsonschema import RefResolver


class GalleonModule(ProcessModule):

    def __init__(self, config, schema, mapping, destination="data"):
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
    
    def consume(self, event):
        raw_data = event.dump()
        try:
            mapped_data = self.mapper.apply(raw_data.get('data'))
            if mapped_data:
                event.set(mapped_data, event.kwargs.destination)
        except Exception as e:
            self.logging.error(
                "Element {} is not mapped. skipping. Reason: {}".format(
                    raw_data.get('id', ''), e
                    )
                )
        self.submit(event, "outbox")