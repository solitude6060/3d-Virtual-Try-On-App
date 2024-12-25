pip install fastapi uvicorn
# uvicorn image_to_3d_api:app --host 0.0.0.0 --port 9100 --reload
uvicorn image_to_3d_api_release_gpu:app --host 0.0.0.0 --port 9100 --reload

