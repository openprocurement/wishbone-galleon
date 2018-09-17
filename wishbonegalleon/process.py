""" wishbonegalleon - Wishbone Encode modules to use galleon transforms """
import ujson
import yaml
from jsonschema import RefResolver
from galleon import Mapper
from wishbone.module import ProcessModule
from .utils import PROCESSORS, load_datafile
from .filters import FILTERS


class GalleonModule(ProcessModule):
    """ Wishbone process module based on galleon transformations """
    def __init__(
            self,
            config,
            schema,
            mapping,
            processors=['ocds', 'hashid'],
            with_hash=False,
            filters=['test'],
            destination="data",
            selection="data"
    ):
        ProcessModule.__init__(self, config)
        for name in ['inbox', 'outbox']:
            self.pool.createQueue(name)
        self.registerConsumer(self.consume, "inbox")
        if not isinstance(mapping, dict):
            mapping = load_datafile(mapping)
        if not isinstance(schema, dict):
            schema = load_datafile(schema)

        self.mapper = Mapper(mapping, RefResolver.from_schema(schema))
        self.filters = [
            FILTERS[name] for name in filters
            if name in FILTERS
        ]
        self.processors = [
            PROCESSORS[name] for name in processors
            if name in PROCESSORS
        ]

    def consume(self, event):
        """ Consume event, process it and push to output queue """
        input_data = event.get(self.kwargs.selection)
        if not input_data:
            return
        try:
            if self.filters:
                for filterfunc in self.filters:
                    if not filterfunc(self, input_data):
                        return
            data = self.mapper.apply(input_data)
            if data:
                if self.processors:
                    for processor in self.processors:
                        data = processor(self, data)
                event.set(data, event.kwargs.destination)
                self.submit(event, "outbox")
            else:
                self.logging.info(
                    "Empty data. skipping"
                    )
        except Exception as e:
            self.logging.error(
                "Event {} raised error, skipping. Reason: {}".format(
                    input_data.get('id', ''), e
                    )
                )
