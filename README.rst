===============================
Autonom - The Ansible task runner for AWS IoT
===============================

Quick Start
-----------
First, install the library:

.. code-block:: sh

    $ pip3 install .

Next, set up a configuration file (in e.g. ``~/.autonom/config.json``):

.. code-block:: json

    {
      "thing_name": "AWS IOT THING NAME",
      "host_name": "AWS IOT HOST NAME",
      "ca_path": "AWS IOT ROOT CA PATH",
      "key_path": "AWS IOT PRIVATE KEY PATH",
      "cert_path": "AWS IOT CERTIFICATE PATH"
    }

Then, run the script:

.. code-block:: sh

    $ autonom

Job Document Format
-----------
.. code-block:: json

    {
      "tasks": [
        {
          "debug": {
            "var": "name"
          }
        }
      ],
      "vars": {
        "name": "value"
      }
    }

For Developers
-----------
First, install Poetry and install requirements:

.. code-block:: sh

    $ pyenv install 3.7.3
    $ pyenv global 3.7.3
    $ curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
    $ poetry install
