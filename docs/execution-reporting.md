# Execution Reporting Guide

How agents report Intent execution results to Validators.

## Overview

After an Agent completes an Intent execution, it must report the results to Validators for verification. The reporting flow is:

```
Agent → ExecutionReport → Validator → Verification → RootLayer
```

## Execution Report Structure

### Core Fields

```go
type ExecutionReport struct {
    // Identifiers
    ReportID     string                     // Unique report ID (required)
    AssignmentID string                     // Task assignment ID (required)
    IntentID     string                     // Original intent ID (required)
    AgentID      string                     // Reporting agent ID (optional, defaults to config.AgentID)

    // Status / timing
    Status    ExecutionReportStatus         // success, failed, partial, or status_unspecified
    Timestamp time.Time                     // Completion timestamp (defaults to now)

    // Results
    ResultData []byte                       // Execution output payload
    Metadata   map[string]string            // Additional key/value context (optional)
}

type ExecutionReportStatus string

const (
    ExecutionReportStatusSuccess     ExecutionReportStatus = "success"
    ExecutionReportStatusFailed      ExecutionReportStatus = "failed"
    ExecutionReportStatusPartial     ExecutionReportStatus = "partial"
    ExecutionReportStatusUnspecified ExecutionReportStatus = "status_unspecified"
)

type ExecutionReceipt struct {
    ReportID    string    // Report acknowledged by validator
    IntentID    string    // Intent ID for traceability
    ValidatorID string    // Validator that processed the report
    Status      string    // Validator status string
    ReceivedAt  time.Time // When the validator accepted the report
    Message     string    // Optional validator message
    Endpoint    string    // HTTP endpoint used for submission
}
```

## Reporting Flow

### Step 1: Execute the Intent

```go
// Go
func (h *Handler) Execute(ctx context.Context, task *Task) (*Result, error) {
    // Record start time
    startTime := time.Now()

    // Execute the task
    output, err := h.processTask(task)

    // Record execution time
    execTime := time.Since(startTime)

    // Collect evidence
    evidence := h.collectEvidence(task, output, execTime)

    return &Result{
        Data:     output,
        Evidence: evidence,
        Success:  err == nil,
        Error:    err,
    }, nil
}
```

```python
# Python
async def execute(self, task: Task) -> Result:
    # Record start time
    start_time = time.time()

    # Execute the task
    try:
        output = await self.process_task(task)
        success = True
        error = None
    except Exception as e:
        output = b""
        success = False
        error = str(e)

    # Record execution time
    exec_time = time.time() - start_time

    # Collect evidence
    evidence = self.collect_evidence(task, output, exec_time)

    return Result(
        data=output,
        evidence=evidence,
        success=success,
        error=error
    )
```

### Step 2: Build Execution Report

```go
// Go
func buildExecutionReport(task *Task, result *Result, agentID string) *ExecutionReport {
    metadata := map[string]string{
        "task_type": task.Type,
    }

    if result.Error != "" {
        metadata["error"] = result.Error
    }

    report := &ExecutionReport{
        ReportID:     generateReportID(),
        AssignmentID: task.ID,
        IntentID:     task.IntentID,
        AgentID:      agentID,
        Status:       ExecutionReportStatusSuccess,
        Timestamp:    time.Now(),
        ResultData:   result.Data,
        Metadata:     metadata,
    }

    if !result.Success {
        report.Status = ExecutionReportStatusFailed
    }

    return report
}
```

```python
# Python
def build_execution_report(task: Task, result: Result, agent_id: str) -> ExecutionReport:
    report = ExecutionReport(
        report_id=generate_report_id(),
        assignment_id=task.id,
        intent_id=task.intent_id,
        agent_id=agent_id,
        timestamp=int(time.time()),
        result_data=result.data,
        result_hash=hash_data(result.data)
    )

    # Set status
    if result.success:
        report.status = ExecutionStatus.SUCCESS
    else:
        report.status = ExecutionStatus.FAILED
        report.error = ErrorInfo(
            code="EXEC_FAILED",
            message=result.error
        )

    # Add evidence
    report.evidence = result.evidence

    return report
```

### Step 3: (Optional) Attach Signatures

Canonical signing for execution reports is still being standardised. If your integration needs provenance today, hash a deterministic payload (for example, `hash(report.ReportID || report.IntentID || report.ResultData)`) and sign it using `sdk.Sign(data)`. Store the signature inside `report.Metadata["agent_signature"]` so validators echo it back in receipts and off-chain monitors can verify authenticity.

### Step 4: Submit to Validators

```go
// Go
receipts, err := sdk.SubmitExecutionReport(ctx, report)
if err != nil {
    return nil, fmt.Errorf("failed to submit report: %w", err)
}

for _, receipt := range receipts {
    log.Printf("validator %s acknowledged report %s", receipt.ValidatorID, receipt.ReportID)
}
```

`SubmitExecutionReport` will:

1. Use `DiscoverValidators` (via the configured `registry_addr`) to fetch all active validator endpoints.
2. Fall back to `validator_addr` from the config when the registry is unavailable.
3. POST the execution report to each validator's `/api/v1/execution-report` HTTP endpoint with retries handled by the caller.

Each successful submission returns an `ExecutionReceipt` containing the validator ID, status, and reception timestamp. When some validators fail, the method returns partial receipts together with a combined error so operators can implement custom retry logic.

## Complete Example

### Go Implementation

```go
package main

import (
    "context"
    "encoding/hex"
    "fmt"
    "log"
    sdk "github.com/pinai/subnet-sdk-go"
)

type ReportingHandler struct {
    sdk *sdk.SDK
}

func (h *ReportingHandler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
    // 1. Execute task
    result, err := h.processTask(task)
    if err != nil {
        return nil, err
    }

    // 2. Build execution report
    report := h.buildReport(task, result)

    // 3. Optionally attach signature metadata
    attachAgentSignature(h.sdk, report)

    // 4. Submit to validators (handles discovery + fanout)
    receipts, err := h.sdk.SubmitExecutionReport(ctx, report)
    if err != nil {
        log.Printf("report submission completed with warnings: %v", err)
    }

    for _, receipt := range receipts {
        log.Printf("validator %s accepted report %s", receipt.ValidatorID, receipt.ReportID)
    }

    return result, nil
}

func attachAgentSignature(sdk *sdk.SDK, report *sdk.ExecutionReport) {
    if sdk.GetAddress() == "" {
        return
    }

    payload := []byte(report.ReportID + report.IntentID)
    sig, err := sdk.Sign(payload)
    if err != nil {
        log.Printf("failed to sign report: %v", err)
        return
    }

    if report.Metadata == nil {
        report.Metadata = map[string]string{}
    }
    report.Metadata["agent_signature"] = fmt.Sprintf("0x%s", hex.EncodeToString(sig))
}
```

## Evidence Collection

> Note: The sections below describe the planned, not-yet-implemented evidence pipeline.


### What to Include

1. **Execution Proof**: Cryptographic proof of execution
2. **Environment Fingerprint**: System state during execution
3. **Input/Output Hashes**: For data integrity
4. **Resource Usage**: CPU, memory, I/O metrics
5. **Transcript Root**: For large outputs

### Example Evidence Collection

```go
func collectEvidence(task *Task, output []byte, execTime time.Duration) *ExecutionEvidence {
    return &ExecutionEvidence{
        ProofExec:      generateExecutionProof(task, output),
        EnvFingerprint: getEnvironmentFingerprint(),
        InputsHash:     hashData(task.Data),
        OutputsHash:    hashData(output),
        ResourceUsage: &ResourceUsage{
            CpuMs:        uint64(execTime.Milliseconds()),
            MemoryMb:     getMemoryUsage(),
            IoOps:        getIOOperations(),
            NetworkBytes: getNetworkBytes(),
        },
    }
}
```

## Validator Verification

Validators perform several checks on execution reports:

1. **Signature Verification**: Verify agent's signature
2. **Timestamp Validation**: Check execution time is reasonable
3. **Evidence Validation**: Verify proofs and hashes
4. **Status Consistency**: Ensure status matches result data
5. **Resource Usage**: Check for reasonable resource consumption

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `InvalidArgument` | Malformed report | Check all required fields |
| `ResourceExhausted` | Rate limit exceeded | Implement backoff |
| `DeadlineExceeded` | Timeout | Increase timeout or optimize |
| `Unauthenticated` | Invalid signature | Check private key |
| `Internal` | Validator error | Retry with backoff |

### Retry Strategy

```go
func reportWithRetry(ctx context.Context, sdk *SDK, report *ExecutionReport) ([]*ExecutionReceipt, error) {
    maxRetries := 3
    backoff := time.Second

    for i := 0; i < maxRetries; i++ {
        receipts, err := sdk.SubmitExecutionReport(ctx, report)
        if err == nil {
            return receipts, nil
        }

        if !isRetryable(err) {
            return receipts, err
        }

        time.Sleep(backoff)
        backoff *= 2
    }

    return nil, fmt.Errorf("max retries exceeded")
}
```

## Best Practices

1. **Always Report**: Report even failed executions
2. **Include Evidence**: Provide comprehensive evidence
3. **Sign Reports**: Always sign with agent's private key
4. **Handle Failures**: Implement retry with backoff
5. **Log Everything**: Keep audit trail of reports
6. **Validate Locally**: Check report before submission
7. **Monitor Metrics**: Track reporting success rate

## Configuration

Add validator endpoint to SDK configuration:

```go
// Go
config, _ := sdk.NewConfigBuilder().
    WithSubnetID("subnet-1").
    WithAgentID("agent-1").
    WithValidatorAddr("validator.example.com:9090").  // Add this
    WithMatcherAddr("matcher.example.com:8090").
    Build()
```

```python
# Python
config = (
    ConfigBuilder()
    .with_subnet_id("subnet-1")
    .with_agent_id("agent-1")
    .with_validator_addr("validator.example.com:9090")  # Add this
    .with_matcher_addr("matcher.example.com:8090")
    .build()
)
```

## Security Considerations

1. **Private Key Security**: Never expose private keys
2. **TLS Connection**: Use TLS for validator connection
3. **Report Tampering**: Reports are signed to prevent tampering
4. **Replay Attacks**: Include nonce or timestamp
5. **Rate Limiting**: Respect validator rate limits

## Next Steps

1. Implement evidence collection for your task types
2. Set up monitoring for report success rates
3. Configure proper timeout and retry policies
4. Test with validator in different scenarios
