""" wishbonegalleon - Wishbone Encode modules to use galleon transforms """
import json
import yaml
from gevent.threadpool import ThreadPoolExecutor
from wishbone.module import ProcessModule
from jsonschema import RefResolver
from galleon import Mapper
from .utils import TAGGERS


class GalleonModule(ProcessModule):
    """ Wishbone process module based on galleon transformations """
    def __init__(
            self,
            config,
            schema,
            mapping,
            tagger="",
            destination="data",
            use_threads=False,
            max_workers=4
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
        self.use_threads = use_threads
        if self.use_threads:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)

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
                if self.use_threads:
                    job = self.executor.submit(self.mapper.apply, (raw_data,))
                    data = job.result()
                else:
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
        
