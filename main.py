import asyncio

from utils.cli import parse_args

asyncio.get_event_loop().run_until_complete(parse_args())