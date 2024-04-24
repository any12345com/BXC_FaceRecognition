ffmpeg -re -stream_loop -1  -i all_images.mp4  -rtsp_transport tcp -c copy -f rtsp rtsp://127.0.0.1:9554/live/all_images
cmd