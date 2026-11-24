"""Launch a local HTTP server and open the 3D visualizer in the browser."""
from __future__ import annotations

import http.server
import os
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 8765


def main() -> None:
    os.chdir(ROOT)

    handler = http.server.SimpleHTTPRequestHandler
    handler.extensions_map.update({".js": "application/javascript"})

    server = http.server.HTTPServer(("", PORT), handler)
    print(f"Serving at http://localhost:{PORT}")
    print(f"Opening visualizer...")
    print("Press Ctrl+C to stop.\n")

    url = f"http://localhost:{PORT}/visualizer/index.html"
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
