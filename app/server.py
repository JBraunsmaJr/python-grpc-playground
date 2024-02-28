import logging
import os
from concurrent import futures
from typing import Iterable, AsyncIterable
import asyncio

import grpc

from generated.file_transfers.file_transfers_pb2 import TransferResponse, FileTransfer, FileInfo, Chunk
from generated.file_transfers.file_transfers_pb2_grpc import (TransferServiceServicer,
                                                              TransferServiceStub,
                                                              add_TransferServiceServicer_to_server)

CHUNK_SIZE = 1024 * 1024  # 1MB
logging.basicConfig()
logger = logging.getLogger(__name__)


def split_file(filepath: str):
    """
    Split a file into 1MB blocks to send over the wire
    :param filepath: Path to file to be split
    :return: Yields file chunks
    """
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return

    file_size = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    # This is the first bit of info about the content to be shipped
    yield FileTransfer(fileInfo=FileInfo(totalLength=file_size, filename=filename))

    try:
        with open(filepath, 'rb') as file:
            while True:
                chunk = file.read(CHUNK_SIZE)

                if len(chunk) == 0:
                    return

                """
                Need to remember that gRPC types that are generated require
                keyword arguments NOT POSITIONAL
                """
                yield FileTransfer(buffer=Chunk(buffer=chunk))
    except Exception as ex:
        logger.error(ex)


async def save_chunks_to_file(directory: str, chunks: AsyncIterable[FileTransfer]) -> tuple[int, int]:
    """
    Stitch together chunks into a single file
    :param directory: Directory to save to
    :param chunks: Chunks needing to be saved
    :return:
    """
    if not chunks:
        return -1, -1

    """
        Chunks / request_iterator is not subscribable. AKA cannot do something like 
        chunks[0] <--- not allowed
        Might be a better alternative to grabbing the initial set of data we want/need
        for saving
    """

    is_first = True
    intended_length: int = -1
    length: int = 0
    pointer = None

    try:
        async for transfer_item in chunks:
            logger.info(transfer_item)
            if is_first and transfer_item.fileInfo is not None:
                is_first = False
                file_path = os.path.join(directory, transfer_item.fileInfo.filename)
                intended_length = transfer_item.fileInfo.totalLength
                pointer = open(file_path, "wb")
                continue

            if transfer_item.buffer is not None:
                pointer.write(transfer_item.buffer.buffer)
                length += len(transfer_item.buffer.buffer)
    except Exception as ex:
        logger.error(ex)
    finally:
        if pointer is not None:
            pointer.close()

    return length, intended_length


class TransferServer(TransferServiceServicer):
    def __init__(self, storage_directory: str):
        self.__storage_dir = storage_directory

        # Create directory if it doesn't exist
        if not os.path.exists(self.__storage_dir):
            os.makedirs(self.__storage_dir)

    async def Transfer(self,
                       request_iterator: AsyncIterable[FileTransfer],
                       context: grpc.aio.ServicerContext):
        logger.info("Started transfer on server")
        try:

            length, intended = await save_chunks_to_file(self.__storage_dir, request_iterator)

            # Again, type requires keyword arguments, not positional
            return TransferResponse(length=length,
                                    statusCode=200 if length == intended else 500,
                                    message="Missing segment" if length != intended else None)
        except Exception as ex:
            logger.error(f"An error occurred while receiving file transfer:\n\t{ex}")
            return TransferResponse(length=-1,
                                    statusCode=500,
                                    message=f"An error occurred during transfer: {ex}")


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


async def start_transfer_grpc_server(port: int):
    server = grpc.aio.server()
    add_TransferServiceServicer_to_server(
        TransferServer(os.path.join(SCRIPT_DIR, "..", "downloads")),
        server
    )
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    await server.wait_for_termination()


async def transfer_file(filepath: str, server_address: str):
    try:
        async with grpc.aio.insecure_channel(server_address) as channel:
            stub = TransferServiceStub(channel)
            response = await stub.Transfer(split_file(filepath))
            print(response)

            if isinstance(response, TransferResponse):
                print(f"Length: {response.length}, status: {response.statusCode}, Message: {response.message}")

    except Exception as ex:
        logger.error(f"An error occurred while transferring {filepath}:\n\t{ex}")
