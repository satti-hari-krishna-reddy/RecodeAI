# Builder stage
FROM openjdk:21-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    golang wget build-essential ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download Ghidra and move it to ghidra_local as ghidra_10.1_PUBLIC before building the image
COPY ghidra_10.1_PUBLIC /app/ghidra_10.1_PUBLIC

COPY ghidra-headless /app/ghidra-headless
COPY ghidra_service.go /app/

RUN mkdir -p /app/binary /app/MyProjDir && chmod 777 /app/binary /app/MyProjDir

RUN go mod init ghidra_service && go mod tidy

# Compile the Go service
RUN go build -o ghidra_service ghidra_service.go

# Final stage
FROM openjdk:21-slim

WORKDIR /app

COPY --from=builder /app/ghidra_10.1_PUBLIC /app/ghidra_10.1_PUBLIC
COPY --from=builder /app/ghidra-headless /app/ghidra-headless
COPY --from=builder /app/ghidra_service /app/ghidra_service
COPY --from=builder /app/binary /app/binary
COPY --from=builder /app/MyProjDir /app/MyProjDir
COPY .env /app/.env
# Install Python runtime for Ghidra scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 5000

# Run the pre-compiled Go service binary
CMD ["./ghidra_service"]