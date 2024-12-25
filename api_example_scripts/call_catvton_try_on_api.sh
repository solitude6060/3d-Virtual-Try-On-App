curl -X POST "http://solitude6060.asuscomm.com:9200/swap" \ # please change to your api
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "person_image=@../imgs/try_on_targets/example.jpeg" \
  -F "cloth_image=@../imgs/try_on_garments/example_cloth.jpg" \
  -F "cloth_type=upper" \
#   -F "mask=@/path/to/mask_image.jpg"  # 如果沒有 mask，可以省略這行
