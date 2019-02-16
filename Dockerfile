FROM mhart/alpine-node:10.15.3

WORKDIR /usr/src/app
COPY . .
RUN npm install 
ENV PATH $PATH:/usr/src/app/node_modules/.bin
RUN webpack --config webpack.config.js --progress --colors && \
    rm -rf /usr/src/app/node_modules

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add --update --no-cache mariadb-client-libs nano && \
    apk add --no-cache --virtual .build-deps mariadb-dev gcc musl-dev python3-dev

RUN pip3 install -r requirements.txt && \
    apk del .build-deps
