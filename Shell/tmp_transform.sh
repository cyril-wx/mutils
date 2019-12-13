#!/bin/bash

while read LINE
do 
	res=$(echo "scale=2; ((9/5) * $LINE) + 32" | bc)
	echo $res
done
