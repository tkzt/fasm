#!/bin/bash

NAME=fasm

echo "Building $NAME..."

VERSION=$(perl -nle 'print $1 if /version = "([^"]+)"/ and !$seen++' pyproject.toml)

# Make sure the version is not empty
if [ -z "$VERSION" ]; then
  echo "Failed to get the version from pyproject.toml"
  exit 1
fi

# Build the image
docker buildx build --platform linux/amd64 -t $NAME:v$VERSION . --no-cache

# Make sure the image is built successfully
if [ $? -ne 0 ]; then
  echo "Failed to build $NAME:v$VERSION"
  exit 1
fi

# Save the image to a tar file
TAR_NAME=$NAME"_v$VERSION".tar
docker save -o $TAR_NAME $NAME:v$VERSION

# Make sure the image is built successfully
if [ $? -ne 0 ]; then
  echo "Failed to export $TAR_NAME.tar"
  exit 1
fi

# Compress the tar file to a tar.gz file
gzip -f $TAR_NAME

echo "Successfully built $NAME:v$VERSION"
