FROM docker.io/arm64v8/alpine:3

ENV MAVP2P_VERSION=0.7.0
WORKDIR /app

RUN apk add wget tar

RUN wget https://github.com/aler9/mavp2p/releases/download/v${MAVP2P_VERSION}/mavp2p_v${MAVP2P_VERSION}_linux_arm7.tar.gz \
 && tar -xvzf mavp2p*.tar.gz \
 && rm mavp2p*.tar.gz

ENTRYPOINT ["/app/mavp2p"]
