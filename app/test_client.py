from server import transfer_file
import os
import asyncio
from timeit import default_timer as timer

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
test_file_to_transfer = os.path.join(SCRIPT_DIR, "..", "Readme.md")


async def main():
    start = timer()
    await transfer_file(test_file_to_transfer, "localhost:5000")
    end = timer()
    print(f"Transferred {os.path.basename(test_file_to_transfer)} in {(end-start):<15}")

if __name__ == "__main__":
    asyncio.run(main())
