# gRPC Test

Personally, never used gRPC with python. 

This project is just me trying to do something super basic with
gRPC, so I can apply it in other places.

----

## Setup

If on Windows, use Git Bash or WSL. Be sure to be within the
virtual environment

```bash
python -m pip install virtualenv
virtualenv .venv

# Windows path
source ./.venv/Scripts/activate

# Paths on other OS's
source ./.venv/bin/activate

# Install the required tools
pip install -r requirements.txt

./protogen.sh

# whenever you're done you can run
deactivate
```