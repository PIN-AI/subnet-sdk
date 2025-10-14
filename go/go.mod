module github.com/PIN-AI/subnet-sdk/go

go 1.24.0

toolchain go1.24.7

require (
	github.com/ethereum/go-ethereum v1.16.4
	google.golang.org/grpc v1.75.0
	google.golang.org/protobuf v1.36.8
	subnet v0.0.0-00010101000000-000000000000
)

require (
	github.com/decred/dcrd/dcrec/secp256k1/v4 v4.0.1 // indirect
	github.com/holiman/uint256 v1.3.2 // indirect
	golang.org/x/crypto v0.39.0 // indirect
	golang.org/x/net v0.41.0 // indirect
	golang.org/x/sys v0.36.0 // indirect
	golang.org/x/text v0.26.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20250707201910-8d1bb00bc6a7 // indirect
)

// Proto files use "subnet/proto/subnet" as go_package, point to SDK itself
replace subnet => ./
