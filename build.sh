#!/bin/bash
# Build script for Render

# Install system dependencies for Pillow
apt-get update
apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev

# Install Python dependencies
pip install -r requirements.txt
