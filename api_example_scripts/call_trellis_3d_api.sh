curl -X POST "http://solitude6060.asuscomm.com:9100/process-image/" \ # please change to your api path
     -H "Content-Type: application/json" \
     -d '{"image_path": "3d_targets/example.webp", "return_type": "gaussian"}'

