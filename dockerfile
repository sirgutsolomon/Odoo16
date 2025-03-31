FROM ubuntu:22.04

USER root

# Update package list and install dependencies, including Python dev headers
RUN apt update && \
    apt install -y software-properties-common wget libpq-dev build-essential python3.10-dev libldap2-dev libsasl2-dev && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.10 python3.10-distutils


# Install pip for Python 3.10
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

# Verify Python and pip installation
RUN python3.10 --version && \
    python3.10 -m pip --version

# Set working directory
WORKDIR /opt/odoo

# Copy your Odoo code into the container
COPY . /opt/odoo

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages -r /tmp/requirements.txt

# Copy Odoo configuration file
COPY ./odoo.conf /etc/odoo/odoo.conf

# Expose Odoo port
EXPOSE 8068

# Run Odoo with the custom codebase
CMD ["python3", "/opt/odoo/odoo-bin", "--config", "/etc/odoo/odoo.conf"]