ARG ARCH=arm64v8
FROM docker.io/${ARCH}/alpine:3

ARG MAVP2P_ARCH=arm7

ENV MAVP2P_VERSION=0.6.5
WORKDIR /app

RUN apk add wget tar

RUN wget https://github.com/aler9/mavp2p/releases/download/v${MAVP2P_VERSION}/mavp2p_v${MAVP2P_VERSION}_linux_${MAVP2P_ARCH}.tar.gz \
 && tar -xvzf mavp2p*.tar.gz \
 && rm mavp2p*.tar.gz

ENTRYPOINT ["/app/mavp2p"]
