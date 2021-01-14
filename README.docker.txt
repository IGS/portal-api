# Clone the portal-api code from GitHub

    $ git clone https://github.com/ihmpdcc/portal-api

# Build the container

    $ docker build -t portal-api:latest .

# Run the container
docker run -v /home/dolley/portal-docker/portal-api/portal-api:/export/portal-api -ti portal-api

