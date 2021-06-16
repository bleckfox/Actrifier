docker run \
    --name actrifier \
    -p 443:443 \
    -p 80:80 \
    --net=bridge \
    --restart=always \
    -v /home/test-1/actrifier_data:/data \
    -e "TZ=Europe/Moscow" \
    --user $(id -u):$(id -g) \
    -d actrifier:latest