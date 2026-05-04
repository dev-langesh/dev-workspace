#!/bin/bash
set -e

# Professional Multi-Distro Test Runner
# Verifies automatic dependency installation across different Linux families.

DISTROS=("ubuntu:24.04" "debian:12")

for DISTRO in "${DISTROS[@]}"; do
    TAG=$(echo "workspace-compat-${DISTRO}" | tr '/' '-' | tr ':' '-')
    echo "----------------------------------------------------------"
    echo "🧪 Testing on: $DISTRO"
    echo "----------------------------------------------------------"

    # Build the test image if it doesn't exist
    if [[ "$(docker images -q "$TAG" 2> /dev/null)" == "" ]]; then
        echo "[*] Building clean test image $TAG..."
        
        cat <<'EOF' > Dockerfile.test
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
WORKDIR /test_app
COPY requirements.txt requirements-test.txt ./

# Install basic environment tools. gocryptfs is NOT installed here.
RUN if command -v apt-get &> /dev/null; then \
        apt-get update && apt-get install -y python3 python3-pip sudo kmod fuse3 ; \
    elif command -v dnf &> /dev/null; then \
        dnf upgrade -y; \
        dnf install -y python3 python3-pip sudo kmod fuse; \
    elif command -v yum &> /dev/null; then \
        yum update -y; \
        yum install -y python3 python3-pip sudo kmod fuse; \
    elif command -v pacman &> /dev/null; then \
        pacman -Syu --noconfirm python python-pip sudo kmod fuse; \
    elif command -v zypper &> /dev/null; then \
        zypper install -y python3 python3-pip sudo kmod fuse openssh; \
    fi

# install virtualenv
RUN python3 -m pip install --break-system-packages virtualenv

# Setup Python environment
RUN python3 -m virtualenv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt -r requirements-test.txt
EOF
        docker build --build-arg BASE_IMAGE="$DISTRO" -t "$TAG" -f Dockerfile.test .
        rm -f Dockerfile.test
    fi

    echo "[*] Running tests on $TAG..."
    docker run --rm --privileged \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$(pwd):/test_app" \
        -w /test_app \
        "$TAG" \
        /bin/bash -c "
            export PYTHONPATH=\$PYTHONPATH:\$(pwd) && \
            /opt/venv/bin/pytest --cov=src tests/
        "
done

echo "✅ Multi-distro validation complete!"
