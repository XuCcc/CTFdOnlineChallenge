#!/bin/sh
docker build -t "pwn" .
docker run -d -p 9999:9999 --name="pwn" pwn
