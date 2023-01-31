Client
=============

.. automodule:: client_2

.. autoclass:: Client
    :members:

Client database
_______________________________

Includes creation of 3 tables.

* Contacts.
* Message history.
* Contact list.

Client window
_______________________________

.. automodule:: client_window

.. autoclass:: Ui_chatWindow
    :members:

.. autoclass:: Ui_Dialog
    :members:

Server
=============

.. automodule:: server

.. autoclass:: Server
    :members:

Server database
_______________________________

Includes creation of 4 tables.

* Client.
* Client history.
* Client list.
* Client password.

Server window
_______________________________

.. automodule:: main_window

.. autoclass:: Ui_MainWindow
    :members:

Logs
=============

Packet includes configs for client and server logging.

* client_log_config.py содержит конфигурацию клиентского логгера.
* server_log_config.py содержит конфигурацию серверного логгера.

Descriptor
=============

.. automodule:: descriptor

.. autoclass:: Port
    :members:

Metaclasses
=============

.. automodule:: Metaclasses

.. autoclass:: ClientVerify
    :members:

.. autoclass:: ServerVerify
    :members:

Launcher
=============

Модуль запуска нескольких клиентов одновременно.
