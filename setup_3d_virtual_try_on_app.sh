#!/bin/bash

# 設定變數
GITHUB_REPO="https://github.com/solitude6060/3d-Virtual-Try-On-App.git"
CLONE_DIR="3d-Virtual-Try-On-App"
NETWORK_NAME="virtual-try-on-net"

# 先 git clone
if [ ! -d "$CLONE_DIR" ]; then
  echo "[INFO] Cloning repository: $GITHUB_REPO"
  git clone $GITHUB_REPO
else
  echo "[INFO] Repository already cloned"
fi

# 切換到目錄
cd $CLONE_DIR || exit

# 建立 Docker 網絡
if ! docker network ls | grep -q "$NETWORK_NAME"; then
  echo "[INFO] Creating Docker network: $NETWORK_NAME"
  docker network create $NETWORK_NAME
else
  echo "[INFO] Docker network $NETWORK_NAME already exists"
fi

# 部署 CatVTON API
echo "[INFO] Deploying CatVTON API"
CATVTON_IMAGE="solitude6060/3d-virtual-try-on-app-catvton:1.0.0"
CATVTON_CONTAINER="catvton-container"
CATVTON_PORT=9111

if ! docker ps -a | grep -q "$CATVTON_CONTAINER"; then
  docker run --gpus all -dit --name $CATVTON_CONTAINER --network $NETWORK_NAME -p $CATVTON_PORT:$CATVTON_PORT \
    -v $(pwd):/app $CATVTON_IMAGE
else
  echo "[INFO] CatVTON container already exists"
fi

docker exec $CATVTON_CONTAINER bash -c "pip install -r /app/requirements/requirements_catvton.txt"
docker exec $CATVTON_CONTAINER bash -c "cd /app/CatVTON && bash run_api.sh" &

# 部署 TRELLIS API
echo "[INFO] Deploying TRELLIS API"
TRELLIS_IMAGE="solitude6060/3d-virtual-try-on-app-trellis:1.0.0"
TRELLIS_CONTAINER="trellis-container"
TRELLIS_PORT=9112

if ! docker ps -a | grep -q "$TRELLIS_CONTAINER"; then
  docker run --gpus all -dit --name $TRELLIS_CONTAINER --network $NETWORK_NAME -p $TRELLIS_PORT:$TRELLIS_PORT \
    -v $(pwd):/app $TRELLIS_IMAGE
else
  echo "[INFO] TRELLIS container already exists"
fi

docker exec $TRELLIS_CONTAINER bash -c "pip install -r /app/requirements/requirements_trellis.txt"
docker exec $TRELLIS_CONTAINER bash -c "cd /app/TRELLIS && bash run_api.sh" &

# 部署 Gradio App
echo "[INFO] Deploying Gradio App"
GRADIO_IMAGE="python:3.10"
GRADIO_CONTAINER="gradio-container"
GRADIO_PORT=9113

if ! docker ps -a | grep -q "$GRADIO_CONTAINER"; then
  docker run -dit --name $GRADIO_CONTAINER --network $NETWORK_NAME -p $GRADIO_PORT:$GRADIO_PORT \
    -v $(pwd):/app $GRADIO_IMAGE bash
  docker exec $GRADIO_CONTAINER bash -c "apt-get update && apt-get install -y git && pip install -r /app/requirements/requirements_app.txt"
else
  echo "[INFO] Gradio container already exists"
fi

docker exec $GRADIO_CONTAINER bash -c "cd /app/demo_example_gradio && python app.py"

# 結束
echo "[INFO] All services are deployed."
echo "CatVTON API: http://localhost:$CATVTON_PORT"
echo "TRELLIS API: http://localhost:$TRELLIS_PORT"
echo "Gradio App: http://localhost:$GRADIO_PORT"
echo "Gradio App: Or check console output for port information."
