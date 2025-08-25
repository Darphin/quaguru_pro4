import pytest

from utils.base_session import BaseSession
from config import Server


@pytest.fixture(scope='session')
def service_with_env(env):
    with BaseSession(base_url=Server(env).service) as session:
        yield session