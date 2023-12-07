#!/usr/bin/env bash

while getopts ":p:n:" opt
do
    case $opt in
        p)
            export MODEL_PATH=$OPTARG
            ;;
        n)
            export MODEL_NAMES=$OPTARG
            ;;
        \?) 
            echo "invalid option: -$OPTARG";;
    esac
done

docker-compose up -d --build