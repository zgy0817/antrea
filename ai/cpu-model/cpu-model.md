# Using Docker Volume Mounts for CPU Model in Bigdl Framework

This guide explains how to use Docker volume mounts to make your CPU based LLM model accessible to a Flask app running in a Docker container. By following these steps, you can keep the path to your model in app.py fixed, while still allowing the app to access your model from your local machine.

## Prerequisites

Before you start, ensure you have the following:

- Docker installed on your local machine
- Files with a specific model path configured (as mentioned in your `app.py`)

## Steps

1. **Create a Dockerfile**: Create a Dockerfile for your Flask app. Below is an example Dockerfile:

    ```Dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.9

    # Set the working directory to /app
    WORKDIR /app

    # Copy the current directory contents into the container at /app
    COPY ..

    # Install any needed packages for python3.9
    RUN python3.9 -m pip install --pre --upgrade bigdl-llm[all]

    RUN python3.9 -m pip install Flask transformers torch

    # Run app.py when the container launches
    CMD ["python3.9", "app.py"]
    ```

2. **Build the Docker Image**: Navigate to the directory containing your Dockerfile and build your Docker image using the following command:

    ```bash
    docker build -t llm-cpu-app .
    ```

3. **Run the Docker Container**: Use the `-v` flag to specify a volume mount. Replace `/local-path/model_path` with the path to your model on your local machine and `/container-path` with the path to `model_path` in your app:

    ```bash
    docker run -v /local-path/model_path:/container-path -p 5000:<host_port> my-flask-app
    ```

4. **Access the Flask App**: Your Flask app running in the Docker container can now access the CPU based bigdl model from the path specified in `app.py` while still allowing you to update the model on your local machine.


