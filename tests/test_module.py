from wishbone.event import Event
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter

from wishbonegalleon import GalleonModule


SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "title": {"type": "string"}        
    }
}
MAPPING = {
    "mapping": {
        "name": {
            "src": "name",
        },
        "title": {
            "src": "data.title"
        }
    }
}
DATA = {
    "name": "test",
    "data": {
        "title": "testing"
    }
}


def test_module_galleon():
    config = ActorConfig('galleon', 100, 1, {}, "")
    galleon = GalleonModule(
        config,
        schema=SCHEMA,
        mapping=MAPPING,
    )

    galleon.pool.queue.inbox.disableFallThrough()
    galleon.pool.queue.outbox.disableFallThrough()
    galleon.start()

    e = Event(DATA)
    galleon.pool.queue.inbox.put(e)

    one = getter(galleon.pool.queue.outbox)
    assert one.get() == {"name": "test", "title": "testing"}