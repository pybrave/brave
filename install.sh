#!/usr/bin/env bash
set -euo pipefail

#----------------------------------------------------
# Default configurations
#----------------------------------------------------
IMAGE_SOURCE="dockerhub"  # default
BASE_DIR=$HOME/brave-install


#----------------------------------------------------
# Parse arguments
#----------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dockerhub|--local)
      IMAGE_SOURCE="dockerhub"
      shift
      ;;
    --aliyun)
      IMAGE_SOURCE="aliyun"
      shift
      ;;
    --base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--aliyun|--dockerhub] [--base-dir /path/to/brave]"
      exit 1
      ;;
  esac
done
#----------------------------------------------------
# Select images based on the source
#----------------------------------------------------
if [[ "$IMAGE_SOURCE" == "aliyun" ]]; then
  MYSQL="registry.cn-hangzhou.aliyuncs.com/wybioinfo/mysql:8.0.21"
  BRAVE="registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave"
else
  MYSQL="mysql:8.0.21"
  BRAVE="wybioinfo/pybrave"
fi


#----------------------------------------------------
# Container & directory settings
#----------------------------------------------------
NETWORK=brave-net
MYSQL_CONTAINER=brave-mysql
BRAVE_CONTAINER=brave

#----------------------------------------------------
# MySQL configuration
#----------------------------------------------------
MYSQL_ROOT_PASSWORD=123456
MYSQL_DATABASE=brave

#----------------------------------------------------
# Helper functions for colored logs
#----------------------------------------------------
info() { echo -e "\033[1;34m[INFO]\033[0m $*"; }
success() { echo -e "\033[1;32m[SUCCESS]\033[0m $*"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*"; }

#----------------------------------------------------
# Start process
#----------------------------------------------------
info "Using image source: $IMAGE_SOURCE"
info "Base directory: $BASE_DIR"

[ ! -d "$BASE_DIR" ] &&  mkdir -p "$BASE_DIR"


#----------------------------------------------------
# Pull required images
#----------------------------------------------------
info "Pulling Docker images..."
docker pull "$MYSQL"
docker pull "$BRAVE"

#----------------------------------------------------
# Stop and remove old containers (if any)
#----------------------------------------------------
for c in $MYSQL_CONTAINER $BRAVE_CONTAINER; do
  if docker ps -a --format '{{.Names}}' | grep -q "^$c$"; then
    warn "Stopping and removing existing container: $c"
    docker rm -f "$c" >/dev/null 2>&1 || true
  fi
done

#----------------------------------------------------
# Create Docker network
#----------------------------------------------------
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
  info "Creating network: $NETWORK"
  docker network create "$NETWORK"
else
  info "Network $NETWORK already exists"
fi

#----------------------------------------------------
# Start MySQL container
#----------------------------------------------------
info "Starting MySQL container..."
mkdir -p "$BASE_DIR/mysql"

docker run -d \
  --network "$NETWORK" \
  --name "$MYSQL_CONTAINER" \
  -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
  -e MYSQL_DATABASE="$MYSQL_DATABASE" \
  -e LANG=C.UTF-8 \
  --shm-size=10G \
  -v "$BASE_DIR/mysql:/var/lib/mysql" \
  "$MYSQL" \
  --default-authentication-plugin=mysql_native_password \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_0900_ai_ci \
  --lower-case-table-names=1

#----------------------------------------------------
# Wait for MySQL to become ready
#----------------------------------------------------
info "⏳ Waiting for MySQL to be ready..."
for i in {1..30}; do
  if docker exec "$MYSQL_CONTAINER" mysqladmin ping -h"127.0.0.1" -p"$MYSQL_ROOT_PASSWORD" --silent; then
    success "✅ MySQL is ready!"
    break
  fi
  sleep 2
  [[ $i -eq 30 ]] && error "❌ MySQL failed to start within timeout" && exit 1
done

#----------------------------------------------------
# Start Brave service container
#----------------------------------------------------
info "Starting Brave container..."
mkdir -p "$BASE_DIR"

docker run -d \
  --network "$NETWORK" \
  --name "$BRAVE_CONTAINER" \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$BASE_DIR:$BASE_DIR" \
  --user "$(id -u):$(id -g)" \
  --group-add "$(stat -c '%g' /var/run/docker.sock)" \
  "$BRAVE" \
  brave --mysql-url "root:${MYSQL_ROOT_PASSWORD}@${MYSQL_CONTAINER}:3306/${MYSQL_DATABASE}" \
        --base-dir $BASE_DIR

#----------------------------------------------------
# Display final info
#----------------------------------------------------
success "Brave started successfully!"
info "Access URL: http://localhost:5000"
info "BASE_DIR: $BASE_DIR"
info "View logs: docker logs -f $BRAVE_CONTAINER"
