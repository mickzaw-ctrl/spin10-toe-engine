"""python -m lab  →  start the Research Lab on 0.0.0.0:8000"""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Spin(10) Research Lab")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run("lab.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
