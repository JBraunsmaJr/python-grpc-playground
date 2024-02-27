from server import transfer_file
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
test_file_to_transfer = os.path.join(SCRIPT_DIR, "..", "Readme.md")

transfer_file(test_file_to_transfer, "localhost:5000")
