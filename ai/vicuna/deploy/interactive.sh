#!/usr/bin/env bash

echo ">> Please ask any questions, or press Ctrl+Z to quit..."
printf ">> "

# wait and read for user input
while read -r user_input; do

    # call model and get message content
    output_json=$(curl -s -X POST -d '{"model": "vicuna", "messages": [{"role": "user", "content": "'"${user_input}"'" }]}' \
             -H "Content-Type: application/json" \
             http://0.0.0.0:8000/v1/chat/completions | jq '.choices[0].message.content')
    
    # output with regulations
    echo $output_json | sed 's/^"//;s/"$//' | sed 's/\\"/"/g'

    sleep 0.5
    echo ">> Please ask any questions, or press Ctrl+Z to quit..."
    printf ">> "
done