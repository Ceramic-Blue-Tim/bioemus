#!/bin/bash
for i in {1..9}
do
	echo "Decoding file: $i ..."
	./decode_raster_file --duration 130 --sep ';' --read-file "../exp$i/raster_loopback.csv" --save-file "../exp$i/raster_loopback_decoded.csv"
done