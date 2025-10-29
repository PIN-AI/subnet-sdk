package agentsdk

import (
	"context"
	"crypto/ecdsa"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"

	"github.com/ethereum/go-ethereum/crypto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/metadata"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
)

// Metadata keys must match the Python implementation and Go interceptors
const (
	SignatureKey = "x-signature"
	SignerIDKey  = "x-signer-id"
	TimestampKey = "x-timestamp"
	NonceKey     = "x-nonce"
	ChainIDKey   = "x-chain-id"
)

// SigningConfig holds configuration for metadata signing
type SigningConfig struct {
	PrivateKey *ecdsa.PrivateKey
	Address    string
	ChainID    string
}

// SigningInterceptor implements gRPC client interceptor for signing requests
type SigningInterceptor struct {
	config *SigningConfig
}

// NewSigningInterceptor creates a new signing interceptor
func NewSigningInterceptor(config *SigningConfig) *SigningInterceptor {
	return &SigningInterceptor{config: config}
}

// UnaryInterceptor returns a grpc.UnaryClientInterceptor
func (si *SigningInterceptor) UnaryInterceptor() grpc.UnaryClientInterceptor {
	return func(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
		ctx, err := si.addMetadata(ctx, method, req)
		if err != nil {
			return err
		}
		return invoker(ctx, method, req, reply, cc, opts...)
	}
}

// StreamInterceptor returns a grpc.StreamClientInterceptor
func (si *SigningInterceptor) StreamInterceptor() grpc.StreamClientInterceptor {
	return func(ctx context.Context, desc *grpc.StreamDesc, cc *grpc.ClientConn, method string, streamer grpc.Streamer, opts ...grpc.CallOption) (grpc.ClientStream, error) {
		ctx, err := si.addMetadata(ctx, method, nil)
		if err != nil {
			return nil, err
		}
		return streamer(ctx, desc, cc, method, opts...)
	}
}

// addMetadata adds signing metadata to context
func (si *SigningInterceptor) addMetadata(ctx context.Context, method string, req interface{}) (context.Context, error) {
	timestamp := time.Now().Unix()
	nonce := generateNonce()

	canonical, err := canonicalJSON(si.config.ChainID, method, timestamp, nonce, req)
	if err != nil {
		return ctx, fmt.Errorf("failed to create canonical JSON: %w", err)
	}

	signature, err := signMessage(si.config.PrivateKey, canonical)
	if err != nil {
		return ctx, fmt.Errorf("failed to sign message: %w", err)
	}

	md := metadata.Pairs(
		SignatureKey, hex.EncodeToString(signature),
		SignerIDKey, si.config.Address,
		TimestampKey, fmt.Sprintf("%d", timestamp),
		NonceKey, nonce,
		ChainIDKey, si.config.ChainID,
	)

	return metadata.NewOutgoingContext(ctx, md), nil
}

// generateNonce creates a random nonce
func generateNonce() string {
	b := make([]byte, 16)
	rand.Read(b)
	return hex.EncodeToString(b)
}

// canonicalJSON creates deterministic JSON for signing
func canonicalJSON(chainID, method string, timestamp int64, nonce string, req interface{}) ([]byte, error) {
	payload := map[string]interface{}{
		"chain_id":  chainID,
		"method":    method,
		"timestamp": timestamp,
		"nonce":     nonce,
	}

	// Convert request to JSON
	var requestBody interface{}
	if req != nil {
		if msg, ok := req.(proto.Message); ok {
			// Protobuf message - convert to JSON preserving field names
			jsonBytes, err := protojson.Marshal(msg)
			if err != nil {
				return nil, fmt.Errorf("failed to marshal proto to JSON: %w", err)
			}
			var jsonMap map[string]interface{}
			if err := json.Unmarshal(jsonBytes, &jsonMap); err != nil {
				return nil, fmt.Errorf("failed to unmarshal JSON: %w", err)
			}
			requestBody = jsonMap
		} else {
			requestBody = req
		}
	}

	if requestBody != nil {
		payload["request"] = requestBody
	}

	// Create deterministic JSON (sorted keys, no whitespace)
	return json.Marshal(payload)
}

// signMessage signs data using Keccak256
func signMessage(privateKey *ecdsa.PrivateKey, data []byte) ([]byte, error) {
	if privateKey == nil {
		return nil, fmt.Errorf("no private key configured")
	}

	hash := crypto.Keccak256Hash(data)
	signature, err := crypto.Sign(hash.Bytes(), privateKey)
	if err != nil {
		return nil, fmt.Errorf("failed to sign: %w", err)
	}

	return signature, nil
}

// DialOption creates gRPC dial options with optional signing
func DialOption(target string, signingConfig *SigningConfig, secure bool) (*grpc.ClientConn, error) {
	opts := []grpc.DialOption{}

	if signingConfig != nil {
		interceptor := NewSigningInterceptor(signingConfig)
		opts = append(opts,
			grpc.WithUnaryInterceptor(interceptor.UnaryInterceptor()),
			grpc.WithStreamInterceptor(interceptor.StreamInterceptor()),
		)
	}

	if secure {
		creds := credentials.NewTLS(nil)
		opts = append(opts, grpc.WithTransportCredentials(creds))
	} else {
		opts = append(opts, grpc.WithTransportCredentials(insecure.NewCredentials()))
	}

	// Use non-blocking dial to avoid hanging on connection
	// Connection will be established in background
	return grpc.Dial(target, opts...)
}