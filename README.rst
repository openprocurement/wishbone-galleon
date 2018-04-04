wishbonegalleon
===============

Wishbone Encode modules to use galleon transforms

Example usage
-----

.. code-block:: yaml

   modules:
      input:
        module: wishbone.module.input.generator
        arguments:
        payload:
            data: foo

   galleon:
      module: wishbone.module.process.galleon
        arguments:
        schema: 1.1-schema.json
        mapping: 1.1-pure.yaml
    
   output:
      module: wishbone.module.output.stdout
        arguments:
        colorize: true
            

   routingtable:
    - input.outbox -> galleon.inbox
    - galleon.outbox -> output.inbox


Installation
------------

pip install 'git+https://github.com/openprocurement/wishbone-galleon.git#egg=wishbonegalleon'

Requirements
^^^^^^^^^^^^

See `setup.py`

Compatibility
-------------
Only python3 is currently supported

Licence
-------

Apache License 2.0

Authors
-------

`wishbonegalleon` was written by `yshalenyk <yshalenyk@quintagroup.com>`_.
