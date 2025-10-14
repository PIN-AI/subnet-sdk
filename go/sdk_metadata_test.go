package agentsdk

import (
	"testing"

	"github.com/ethereum/go-ethereum/common"
)

func TestEnsureChainAddressMetadataAddsAddress(t *testing.T) {
	original := map[string]string{"foo": "bar"}
	result := ensureChainAddressMetadata(original, "0xAbC1230000000000000000000000000000000000")

	if _, ok := original[chainAddressMetadataKey]; ok {
		t.Fatalf("expected original map to remain unchanged")
	}

	expected := common.HexToAddress("0xAbC1230000000000000000000000000000000000").Hex()
	if got := result[chainAddressMetadataKey]; got != expected {
		t.Fatalf("unexpected chain address %s", got)
	}

	if result["foo"] != "bar" {
		t.Fatalf("expected metadata to include existing key")
	}
}

func TestEnsureChainAddressMetadataRespectsExistingValue(t *testing.T) {
	existing := map[string]string{chainAddressMetadataKey: "0x1111"}
	result := ensureChainAddressMetadata(existing, "0x2222")

	if result[chainAddressMetadataKey] != "0x1111" {
		t.Fatalf("expected existing chain address to be preserved")
	}
}

func TestEnsureChainAddressMetadataHandlesEmptyInput(t *testing.T) {
	if metadata := ensureChainAddressMetadata(nil, ""); metadata != nil {
		t.Fatalf("expected nil metadata when address empty")
	}
}

func TestConfigValidateChainAddress(t *testing.T) {
	cfg := &Config{
		AgentID:      "agent-1",
		MatcherAddr:  "matcher:8090",
		Capabilities: []string{"compute"},
		ChainAddress: "0xabc1230000000000000000000000000000000000",
	}

	if err := cfg.Validate(); err != nil {
		t.Fatalf("unexpected validation error: %v", err)
	}

	if cfg.ChainAddress != "0xAbc1230000000000000000000000000000000000" {
		t.Fatalf("expected normalized checksum address, got %s", cfg.ChainAddress)
	}
}

func TestConfigValidateChainAddressMismatch(t *testing.T) {
	cfg := &Config{
		AgentID:      "agent-1",
		MatcherAddr:  "matcher:8090",
		Capabilities: []string{"compute"},
		PrivateKey:   "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		ChainAddress: "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
	}

	if err := cfg.Validate(); err != nil {
		t.Fatalf("unexpected validation error: %v", err)
	}

	if _, err := New(cfg); err == nil {
		t.Fatal("expected error for mismatched chain address and private key")
	}
}
