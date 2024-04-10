# This is installing the pgvector extension for postgres
# Inspired from https://github.com/stupid-programmer/docker_postgres_vector_extension
FROM postgres:15-alpine

RUN apk update && apk add\
    build-base \
    git \
    g++ \ 
    make \ 
    clang15 \
    clang-dev \
    gcc \
    musl-dev 

RUN apk add llvm15-dev llvm15

WORKDIR /tmp
RUN git clone https://github.com/pgvector/pgvector.git

WORKDIR /tmp/pgvector
RUN make
RUN make install
