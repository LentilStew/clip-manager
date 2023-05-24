docker volume create data
docker build -f "./Dockerfile-cron" -t ayalaaa/clip-manager-cron:1.0 .
docker run -v data:/data 98eb9a5a560f
docker build -f "./Dockerfile-website" -t ayalaaa/clip-manager-website:1.0 .
sudo docker run -p 8501:8501 3f608fd42c13