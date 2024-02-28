import logging
import os
from concurrent import futures
from typing import List, Iterable

import grpc

from generated.file_transfers.file_transfers_pb2 import TransferResponse, FileChunk
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
                yield FileChunk(length=file_size,
                                filename=filename,
                                buffer=chunk)
    except Exception as ex:
        logger.error(ex)


def save_chunks_to_file(directory: str, chunks: Iterable[FileChunk]) -> tuple[int, int]:
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
    filepath: str = None
    intended_length = None
    length = 0

    file_pointer = None
    try:
        for chunk in chunks:
            if filepath is None:
                filepath = os.path.join(directory, chunk.filename)
                file_pointer = open(filepath, 'wb')
                intended_length = chunk.length
            file_pointer.write(chunk.buffer)
            length += len(chunk.buffer)
    except Exception as ex:
        logger.error(ex)
    # cannot forget to close the file
    finally:
        if file_pointer is not None:
            file_pointer.close()

    return length, intended_length


class TransferServer(TransferServiceServicer):
    def __init__(self, storage_directory: str):
        self.__storage_dir = storage_directory

        # Create directory if it doesn't exist
        if not os.path.exists(self.__storage_dir):
            os.makedirs(self.__storage_dir)

    def Transfer(self,
                 request_iterator: Iterable[FileChunk],
                 context: grpc.ServicerContext):
        logger.info("Started transfer on server")
        try:
            length, intended = save_chunks_to_file(self.__storage_dir, request_iterator)

            # Again, type requires keyword arguments, not positional
            return TransferResponse(length=length,
                                    statusCode=200 if length == intended else 500,
                                    message="Missing segment" if length != intended else None)
        except Exception as ex:
            logger.error(f"An error occurred while receiving file transfer:\n\t{ex}")
            return TransferResponse(length=-1,
                                    statusCode=500,
                                    message="An error occurred during transfer")


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def start_transfer_grpc_server(port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TransferServiceServicer_to_server(
        TransferServer(os.path.join(SCRIPT_DIR, "..", "downloads")),
        server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


def transfer_file(filepath: str, server_address: str):
    try:
        with grpc.insecure_channel(server_address) as channel:
            stub = TransferServiceStub(channel)
            response = stub.Transfer(split_file(filepath))
            print(response)

            if isinstance(response, TransferResponse):
                print(f"Length: {response.length}, status: {response.statusCode}, Message: {response.message}")

    except Exception as ex:
        logger.error(f"An error occurred while transferring {filepath}:\n\t{ex}")
