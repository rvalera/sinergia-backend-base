# SINERGIA - Backend de Servicios REST para Interactuar con Blockchain

SINERGA es una iniciativa centrada en la construccion de un conjunto de servicios web tipo REST desplegados en la forma de Swagger, para consumir y manipular funcionalidades proporcionados por la Blockchain de Substrate, utilizando para ello la interface de interoperabilidad substrate-interface-py de Polkascan, de esta manera, el objetivo es ofrecer un esquema amigable y sencillo para acceder a la logica de negocio que se encuentra en una Blockchain, con ello se presenta al programador un enfoque de desarrollo efectivo al momento de abordar aplicaciones de proposito general que utilicen Blockchain.

Esta propuesta utiliza  [Python Substrate Interface Library](https://github.com/polkascan/py-substrate-interface)

Esto es un Backend basado en Python y Subtrate Python Interface que permite interactuar mediante una interface de usuario basado en Swagger con una Blockchain basada en Substrate

Features:
-------
 - Permite el almacenamiento de objetos en la Blockchain, esto es, Sitios, Contenido y Tipos de Contenido.
 - Permite visualizar y desargar objetos almacenados en la Blockchain.

## Getting Started

Installing (in project folder):

    py -m venv venv
    . venv/Scripts/activate
    # In venv:
    pip install -r requirements.txt
    export CONFIG_TYPE=dev
    py manage.py db_init


Running app:

    # In venv:
    py manage.py run

 And go to: `http://127.0.0.1:5000/api/v1/`

Running tests:

    # In venv
    export CONFIG_TYPE=tests
    py manage.py run_tests

----------
I will be glad to feedback!
