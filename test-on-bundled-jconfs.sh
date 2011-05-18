#!/bin/bash
for f in /usr/share/vrjuggler-3.0/data/configFiles/*.jconf; do
	echo $f
	./jconf2dot.py $f > /dev/null || exit 1
done
