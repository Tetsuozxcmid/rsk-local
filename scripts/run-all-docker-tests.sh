#!/usr/bin/env sh
# Из каталога rsk_local: sh scripts/run-all-docker-tests.sh
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
COMPOSE="$ROOT/docker-compose.tests.yml"

echo "=== docker compose build ==="
docker compose -f "$COMPOSE" build

for s in auth_tests teams_tests user_profile_tests frontend_tests; do
  echo ""
  echo "=== $s ==="
  docker compose -f "$COMPOSE" run --rm "$s"
done

echo ""
echo "Все тесты в Docker прошли успешно."
