# nano-node-builder

For each new commit on [nanocurrency/nano-node](https://github.com/nanocurrency/nano-node) this project builds the corresponding docker-image and publishes it to dockerhub  [gr0v1ty/nano-node](https://hub.docker.com/r/gr0v1ty/nano-node/tags)

## How can I verify you didn't modify the nano_node source code ?

- Building the node and publishing it to dockerhub is done inside a public github workflow.
- The official nanocurrency/nano-node repository is cloned and the official scripts are used to build the dokcer image.
- This can be verified by looking at the github action logs.
- In the last step of the workflow, the docker image is pushed to dockerhub.

This way, I can guarantee that only official source code is pushed to dockerhub.

## How can I run your docker image ?

The docker-tag corresponds to the commit hash inside the nano-node repository.

`gr0v1ty/nano-node:{commit_hash}`

For example :
- If you want to run the nano_node which has the following commit [`154b7fd9a95e5b15b77d8c10e6ee277ff5dab8cb`](https://github.com/nanocurrency/nano-node/commit/154b7fd9a95e5b15b77d8c10e6ee277ff5dab8cb)
- Use the following docker image : `gr0v1ty/nano-node:154b7fd9a95e5b15b77d8c10e6ee277ff5dab8cb`
