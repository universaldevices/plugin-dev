#!/bin/sh
# do 
# eval `dev.init.sh <slot number>`

if [ -z $1 ]
then
	echo "error ... you need the slot numbrer"
	return
fi 
cat /usr/local/etc/rc.d/0021b9262626_$1 | grep PG3INIT 
