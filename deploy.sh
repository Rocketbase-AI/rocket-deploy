#!/usr/bin/env bash

rocket_slug="lucas/yolov3"
tag="0.3"

# build the container
docker build --tag "$rocket_slug:$tag" .

# tag the container
docker tag "$rocket_slug:$tag" "gcr.io/rockethub/rocket/$rocket_slug:$tag"

# upload the container
docker push "gcr.io/rockethub/rocket/$rocket_slug:$tag"

