"""Compatibility entrypoint for hosts that start main.py."""

from app import main


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
