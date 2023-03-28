#!/bin/sh -e

if [ "$#" -eq 0 ]; then
    echo "Illegal number of parameters"
    echo "./build.sh <program-dir> <roofs-filename>"
    echo "or ./build.sh <program-dir> <roofs-filename> <ip-with-mask> <gateway>"
    exit 1
fi

if [ $1 = "help" ]; then
    echo "./build.sh <program-dir> <roofs-filename> <ip-with-mask> <gateway>"
    exit 0
fi

# TODO: docker build -t {{ app_id }} /root/{{ app_id }}
docker build -t app /root/app_docker_template

CODEDIR="$(readlink -f $1)"

if [ "$#" -eq 4 ]; then
	# TODO: docker run --rm --privileged --env IP=$3 --env GATEWAY=$4 -v $CODEDIR:/opt/code {{ app_id }}
    docker run --rm --privileged --env IP=$3 --env GATEWAY=$4 -v $CODEDIR:/opt/code app
fi

if [ "$#" -eq 2 ]; then
	# TODO: docker run --rm --privileged -v $CODEDIR:/opt/code {{ app_id }}
    docker run --rm --privileged -v $CODEDIR:/opt/code app
fi

ROOTFSDIR="$(readlink -f $2)"
mv $CODEDIR/rootfs $ROOTFSDIR

echo "Root filesystem created as: $ROOTFSDIR"
