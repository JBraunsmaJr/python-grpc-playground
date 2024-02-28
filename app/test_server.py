import asyncio
from server import start_transfer_grpc_server


async def main():
    await start_transfer_grpc_server(5000)


if __name__ == "__main__":
    asyncio.run(main())
