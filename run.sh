docker volume create data

docker build -f "./Dockerfile-daily" -t ayalaaa/clip-manager-daily:1.0 .
docker run --dns 8.8.8.8 -v data:/data -it ayalaaa/clip-manager-daily:1.0

docker build -f "./Dockerfile-weekly" -t ayalaaa/clip-manager-weekly:1.0 .
docker run --dns 8.8.8.8 -v data:/data -it ayalaaa/clip-manager-weekly:1.0

docker build -f "./Dockerfile-website" -t ayalaaa/clip-manager-website:1.0 .
sudo docker run -p 8501:8501 -it ayalaaa/clip-manager-website:1.0

