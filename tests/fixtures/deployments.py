import pytest


@pytest.fixture(scope="module")
def anycall(alice, AnyCallProxy):
    return AnyCallProxy.deploy(alice, {"from": alice})
