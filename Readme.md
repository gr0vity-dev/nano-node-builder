# nano-node-builder

This project builds Docker images for [nanocurrency/nano-node](https://github.com/nanocurrency/nano-node) and publishes them to Docker Hub at [gr0v1ty/nano-node](https://hub.docker.com/r/gr0v1ty/nano-node/tags).

Builds and tests use one queue, newest first, regardless of type: landed commits use their landing date, and open PR heads use the PR's latest update date. Every discovered landed commit remains eligible. For open pull requests, automatic builds and continuous tests only select the current head commit reported by GitHub. Older PR commits and closed PRs remain in the history but are skipped by both queues. Each build checks out the exact selected commit, so its Docker tag matches the source that was built.

An already running build or test finishes. After publishing an image and saving its status, the builder dispatches continuous testing and the next build. Each automatic test run dispatches the next test after saving its report. Each queue stops when no eligible work remains. Five-minute build and ten-minute test schedules remain as fallbacks. Images are marked ready only after Docker publishing succeeds. The continuous-testing workflow's manual `build_hash` input can still test an older successful build explicitly without starting more test runs.

Queue selection checks: `python3 -m unittest discover -s tests` (requires `jq`).

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
