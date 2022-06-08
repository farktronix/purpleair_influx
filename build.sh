#!/bin/bash

docker buildx build --platform linux/arm --push -t farktronix/purpleair_influx:latest .
