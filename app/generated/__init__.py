import sys
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
file_transfers = os.path.join(CURRENT_DIR, "file_transfers")
sys.path.append(file_transfers)
