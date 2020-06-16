Chat Service
=============

This project allows a user to simulate a chatting service with multiple terminals on their local device.

Install Additional Libraries
--------------------------------

Use the package manager `pip <https://pip.pypa.io/en/stable/>`__ to
install bidict and keyboard.

.. code:: bash

    pip install bidict
    pip install keyboard

Instructions and Notes
------------------------
- server.py needs to be run first
- Username and passwords cannot contain any whitespace
- You cannot send a message to yourself
- A single account cannot be logged into multiple clients (i.e. terminals)

- The list of users are stored in the text file called listOfUsers.txt which contains two columns. The first is the username and the second is the password.
- Messages sent to users are stored in files in the Users directory.

License
-------

| Copyright © 2020 Aditya Vadlamani.
| This is `MIT <https://choosealicense.com/licenses/mit/>`__ licensed.
