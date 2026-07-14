from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from services.config import *


def obter_engine():

    url = URL.create(
        drivername="mysql+pymysql",
        username=USUARIO,
        password=SENHA,
        host=HOST,
        port=PORTA,
        database=BANCO,
    )

    engine = create_engine(url)

    return engine