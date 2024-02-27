mkdir -p ./app/generated

if [ ! -f "./app/generated/__init__.py" ]; then
  touch ./app/generated/__init__.py
  cat <<EOF
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
EOF >> ./app/generated/__init__.py
fi

for file in ./protos/*.proto; do
  filename=$(basename $file)
  filename=${filename%.*}
  dir="./app/generated/$filename"
  mkdir -p $dir

  # Generate init script for sub dirs
  if [ ! -f "$dir/__init__.py" ]; then
    touch "$dir/__init__.py"

    echo "sys.path.append(os.path.join(CURRENT_DIR, ""$file_transfers""))" >> ./app/generated/__init__.py
  fi

  python -m grpc_tools.protoc -I./protos --python_out="$dir" --pyi_out="$dir" --grpc_python_out="$dir" $file
done
