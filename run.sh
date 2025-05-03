#!/bin/bash

cd $(dirname $0)

pwd

docker compose down || true

docker compose up -d

echo "Done"

echo "run 'mpv http://localhost:8000' to listen to the stream"

exit 0

