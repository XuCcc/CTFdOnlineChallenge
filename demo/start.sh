#!/bin/sh

/etc/init.d/xinetd start;
python /root/send.py;
sleep infinity;
