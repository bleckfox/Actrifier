FROM nginx

VOLUME ["/data"]
COPY ./install_packages.sh /install_packages.sh
COPY ./core/requirements.txt /requirements.txt
RUN bash /install_packages.sh
RUN pip3 install wheel
RUN pip3 install -r requirements.txt
COPY ./core /
COPY ./nginx/conf.d/* /etc/nginx/conf.d/
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
WORKDIR /data
EXPOSE 443
EXPOSE 80
CMD ["python3", "-u", "/app.py"]