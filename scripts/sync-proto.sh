#!/bin/bash
# Sync proto files from pin_protocol repository
#
# Usage:
#   ./scripts/sync-proto.sh              # sync from local pin_protocol
#   ./scripts/sync-proto.sh v0.1.0       # sync from GitHub tag
#   ./scripts/sync-proto.sh main         # sync from GitHub main branch

set -e

VERSION=${1:-"local"}
PIN_PROTOCOL_DIR=${PIN_PROTOCOL_DIR:-"../pin_protocol"}
PROTO_DEST="proto-src/subnet"

echo "=== Proto Sync Tool ==="

if [ "$VERSION" = "local" ]; then
    # Sync from local pin_protocol directory
    if [ ! -d "$PIN_PROTOCOL_DIR" ]; then
        echo "❌ Error: Local pin_protocol not found at $PIN_PROTOCOL_DIR"
        echo "Set PIN_PROTOCOL_DIR environment variable or use: ./sync-proto.sh <version>"
        exit 1
    fi

    echo "📁 Syncing from local: $PIN_PROTOCOL_DIR"
    cp "$PIN_PROTOCOL_DIR/proto/subnet/"*.proto "$PROTO_DEST/"
    echo "✓ Copied $(ls $PROTO_DEST/*.proto | wc -l | tr -d ' ') proto files"

else
    # Download from GitHub
    echo "🌐 Downloading from GitHub (version: $VERSION)..."
    BASE_URL="https://raw.githubusercontent.com/PIN-AI/pin_protocol/$VERSION/proto/subnet"

    mkdir -p "$PROTO_DEST"
    cd "$PROTO_DEST"

    # List of proto files (update when new files are added)
    PROTO_FILES=(
        "agent.proto"
        "bid.proto"
        "checkpoint.proto"
        "execution_report.proto"
        "matcher.proto"
        "matcher_service.proto"
        "registry_service.proto"
        "report.proto"
        "service.proto"
        "validation.proto"
        "validator.proto"
    )

    for file in "${PROTO_FILES[@]}"; do
        echo "  Downloading $file..."
        if ! curl -fsSL "$BASE_URL/$file" -o "$file"; then
            echo "❌ Failed to download $file"
            exit 1
        fi
    done

    cd ../..
    echo "✓ Downloaded ${#PROTO_FILES[@]} proto files"
fi

echo ""
echo "✓ Proto files synced successfully!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff proto-src/"
echo "  2. Regenerate proto: cd go && make proto"
echo "  3. Regenerate proto: cd python && make proto"
echo "  4. Commit: git add proto-src/ && git commit -m 'chore: sync proto to $VERSION'"
