# Start with your base image
FROM  python:3.12.3-slim


WORKDIR /app

# clone repo
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    git clone https://github.com/ocueye2/proxyasasite.git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN pip install requests, bs4

# Make port 8080 available to the world outside this container
EXPOSE 802

WORKDIR /app/proxyasasite
# Run app.py when the container launches
CMD ["python", "proxy.py"]