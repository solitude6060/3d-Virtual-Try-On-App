pip install fastapi uvicorn
# uvicorn cloth_swap_api:app --host 0.0.0.0 --port 9200 --reload
uvicorn cloth_swap_api_release_gpu:app --host 0.0.0.0 --port 9200 --reload

