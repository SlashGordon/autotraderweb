# autotraderweb

autotraderweb is a frontend for the [autotrader](https://github.com/SlashGordon/autotrader) backend.

## Installation

autotraderweb requires [docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) to run.

```sh
$ docker stop $(docker ps -qf "name=autotraderweb") || exit 0
$ docker-compose rm -v --force
$ docker-compose build
$ docker-compose up -d
```
