import os
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    port = os.environ.get("PORT", "8501")
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        port,
        "--server.address",
        "0.0.0.0",
    ]
    sys.exit(stcli.main())
