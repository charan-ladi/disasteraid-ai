"""
conftest.py
Enables pytest-socket plugin. Tests marked @pytest.mark.disable_socket
will fail if they attempt any real network call.
"""

pytest_plugins = ["pytest_socket"]
