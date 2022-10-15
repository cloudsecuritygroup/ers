#!/bin/bash

if [ "$1" == "range_brc" ]; then 
	echo "Running the Range-BRC scheme on the NH dataset."
	python3 -m ers.schemes.benchmark data/nh_32.csv -1 range_brc_3d runquery 100 small
elif [ "$1" == "linear" ]; then 
	echo "Running the Linear scheme on the NH dataset."
	python3 -m ers.schemes.benchmark data/nh_32.csv -1 linear runquery 100 small
elif [ "$1" == "qdag_src" ]; then 
	echo "Running the Qdag-SRC scheme on the NH dataset."
	python3 -m ers.schemes.benchmark data/nh_32.csv -1 qdag_src_3d runquery 100 small
elif [ "$1" == "tdag_src" ]; then 
	echo "Running the Tdag-SRC scheme on the NH dataset."
	python3 -m ers.schemes.benchmark data/nh_32.csv -1 tdag_src_3d runquery 100 small
elif [ "$1" == "quad_brc" ]; then 
	echo "Running the Quad-BRC scheme on the NH dataset."
	python3 -m ers.schemes.benchmark data/nh_32.csv -1 quad_brc_3d runquery 100 small
else {
   # Display Help
   echo "Please specify one of the schemes below as an argument:"
   echo "	- linear"
   echo "	- range_brc"
   echo "	- quad_brc"
   echo "	- qdag_src"
   echo "	- tdag_src"
}
fi
