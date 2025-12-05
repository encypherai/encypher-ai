# Encypher Go SDK Makefile

VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "none")
DATE ?= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

LDFLAGS := -ldflags "-X main.version=$(VERSION) -X main.commit=$(COMMIT) -X main.date=$(DATE)"

.PHONY: all build install clean test

all: build

# Build the CLI binary
build:
	go build $(LDFLAGS) -o bin/encypher ./cmd/encypher

# Install to GOPATH/bin
install:
	go install $(LDFLAGS) ./cmd/encypher

# Build for all platforms
build-all:
	GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o bin/encypher-linux-amd64 ./cmd/encypher
	GOOS=linux GOARCH=arm64 go build $(LDFLAGS) -o bin/encypher-linux-arm64 ./cmd/encypher
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o bin/encypher-darwin-amd64 ./cmd/encypher
	GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o bin/encypher-darwin-arm64 ./cmd/encypher
	GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o bin/encypher-windows-amd64.exe ./cmd/encypher

# Run tests
test:
	go test -v ./...

# Clean build artifacts
clean:
	rm -rf bin/

# Update dependencies
deps:
	go mod tidy
	go mod download
