#!/usr/bin/env bash

user_input="Please give me 3 numbers between 1 and 10"
curl -X POST -d '{"model": "vicuna", "messages": [{"role": "user", "content": "'"${user_input}"'" }]}' \
             -H "Content-Type: application/json" \
             http://0.0.0.0:8000/v1/chat/completions
echo ' '