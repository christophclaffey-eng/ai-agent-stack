#!/usr/bin/env bash
echo "Removing orphan (stopped) containers..."
docker container prune -f
echo "Done."
