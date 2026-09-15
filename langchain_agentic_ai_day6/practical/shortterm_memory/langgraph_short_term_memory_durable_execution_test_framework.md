# LangGraph Agent Short-Term Memory & Durable Execution Test Framework

For the Trade Prematching and KYC Document Extraction agents, the persistence tests should be organized into a formal Short-Term Memory / Persistence Test Suite rather than treated as independent LangGraph features.

## 1. Recommended Test Matrix

| # | Capability | Priority | Trade Prematching | KYC Extraction |
|---|---|---|---|---|
| 1 | Interrupt & Resume | M | ✅ | ✅ |
| 2 | HITL Approve / Reject / Edit | M | ✅ | ⚪ |
| 3 | Tool Interrupt | M | ✅ | ✅ |
| 4 | Tool Failure Recovery | M | ✅ | ✅ |
| 5 | Time Travel | M | ✅ | ✅ |
| 6 | Fault Tolerance / Resume after Failure | M | ✅ | ✅ |
| 7 | Fork / Pending Writes | M | ✅ | ✅ |
| 8 | Replay | M | ✅ | ✅ |
| 9 | Get State | M | ✅ | ✅ |
| 10 | Get State History | O | ✅ | ✅ |
| 11 | Filter State History | O | ✅ | ✅ |
| 12 | Delta Channel | O | Performance | Performance |
| 13 | Saver Operations | M | ✅ | ✅ |
| 14 | Serialization | M | ✅ | ✅ |
| 15 | Encryption / Decryption | M | Security | Security |

Additional recommended tests:

### 16. Concurrent Threads

Run multiple independent executions:

```text
TRD-1001 → thread-A
TRD-1002 → thread-B
TRD-1003 → thread-C
```

Verify that checkpoints never leak between threads.

### 17. Checkpoint Isolation / Tenant Isolation

If the platform supports multiple desks or tenants:

```text
Tenant A
   └── Thread A
       └── checkpoints

Tenant B
   └── Thread B
       └── checkpoints
```

Verify that Tenant A cannot retrieve Tenant B's state.

---

# 2. Test Architecture

Build a **Persistence Test Harness** around the existing LangGraph agents.

```text
                   ┌─────────────────────┐
                   │  Test Harness       │
                   └──────────┬──────────┘
                              │
             ┌────────────────┼─────────────────┐
             │                │                 │
             ▼                ▼                 ▼
       Trade Agent       KYC Agent       Persistence Tests
             │                │                 │
             └────────────────┼─────────────────┘
                              ▼
                    SQLite Checkpointer
                              │
                              ▼
                       Checkpoint Store
```

The key idea is:

**Do not put all testing logic inside the agent.**

Instead, create a reusable test harness exposing operations such as:

```python
invoke()
get_state()
get_history()
resume()
replay()
fork()
inspect_checkpoint()
```

---

# 3. Test 1 — Interrupt and Resume

This should be the first mandatory test.

For Trade Prematching:

```text
Trade Received
      ↓
Validate Trade
      ↓
Enrich Counterparty
      ↓
Determine SSI
      ↓
     HITL
      ↓
Approve / Reject / Edit
      ↓
Prematch
```

Suppose the agent reaches the HITL node and interrupts.

Before interrupt:

```python
state = graph.get_state(config)

assert state.values["trade_id"] == "TRD-1001"
assert state.next == ("human_review",)
```

After supplying human input, the graph should resume from the persisted checkpoint rather than starting from the beginning.

Expected:

```text
human_review
     ↓
prematch
     ↓
complete
```

Important assertion:

> The graph must not start from the beginning after resume.

---

# 4. HITL — Approve / Reject / Edit

Make this three separate test cases.

## Test 1 — Approve

```text
Agent
 ↓
Human Review
 ↓
APPROVE
 ↓
Prematch
```

Expected:

```python
status == "PREMATCHED"
```

## Test 2 — Reject

```text
Agent
 ↓
Human Review
 ↓
REJECT
 ↓
END
```

Expected:

```python
status == "REJECTED"
```

## Test 3 — Edit

For example, the agent produces:

```json
{
  "settlement_location": "EUROCLEAR",
  "quantity": 100
}
```

The human changes it to:

```json
{
  "settlement_location": "DTC",
  "quantity": 100
}
```

Then resume.

Expected flow:

```text
Agent-generated state
        ↓
Human modification
        ↓
Persist modified state
        ↓
Continue
```

This validates that the checkpoint mechanism correctly persists modified state.

---

# 5. Tool Interrupt

Tool interruption is different from HITL.

For example:

```text
Trade Agent
    ↓
get_settlement_instruction()
    ↓
External SSI Service
    ↓
WAIT
```

Test both:

## Success

```text
Agent
 ↓
SSI Tool
 ↓
SUCCESS
 ↓
Prematch
```

## Failure

```text
Agent
 ↓
SSI Tool
 ↓
TIMEOUT / ERROR
 ↓
Checkpoint
 ↓
Resume
 ↓
Retry Tool
```

This tests:

**tool execution + checkpoint persistence + recovery**

---

# 6. Time Travel

This is one of the most important tests for the KYC use case.

Example:

```text
Document Upload
       ↓
OCR
       ↓
Document Classifier
       ↓
Passport
       ↓
Field Extraction
       ↓
Validation
```

Suppose the classifier incorrectly determines:

```text
actual     = Passport
classifier = Driving Licence
```

You might have:

```text
Checkpoint A
Document uploaded

Checkpoint B
OCR completed

Checkpoint C
Classifier = Driving Licence

Checkpoint D
Extraction
```

Go back to:

```text
Checkpoint B
```

and change the workflow:

```text
Checkpoint B
      ↓
Correct classifier
      ↓
Passport extraction
      ↓
Validation
```

The original execution should remain intact.

Conceptually:

```text
Original
A → B → C → D

Fork
     B → Corrected C → Corrected D
```

This distinction is critical for auditability.

---

# 7. Fault Tolerance

This differs from time travel.

Example:

```text
Trade
 ↓
Validate
 ↓
Enrich
 ↓
SSI lookup
 ↓
❌ Node failure
```

The checkpoint before the failed node should exist.

The system should restart from:

```text
SSI lookup
```

rather than re-running:

```text
Trade
 ↓
Validate
 ↓
Enrich
 ↓
SSI lookup
```

Inject a deliberate failure:

```python
raise RuntimeError("Simulated failure")
```

Then:

1. Run the agent.
2. Allow the node to fail.
3. Inspect the checkpoint.
4. Restart.
5. Verify execution resumes from the last successful step.

A strong assertion is to track node execution counts:

```python
execution_count = {
    "validate_trade": 1,
    "enrich_counterparty": 1,
    "get_ssi": 2
}
```

Expected:

```text
validate_trade       → NOT executed again
enrich_counterparty  → NOT executed again
get_ssi              → retried
```

This gives an objective test instead of only checking final output.

---

# 8. Fork / Pending Writes

This is particularly valuable for backtesting.

Suppose:

```text
Checkpoint 100
      ↓
Classifier
      ↓
Prematching
      ↓
Settlement
```

Create an alternate execution:

```text
                    Checkpoint 100
                         │
              ┌──────────┴──────────┐
              │                     │
          Original              Experiment
              │                     │
      Original classifier      New classifier
              │                     │
          Prematch A             Prematch B
```

The original execution should remain untouched.

This enables:

```text
Historical checkpoint
        ↓
       Fork
        ↓
New prompt/model/policy
        ↓
Run remaining graph
        ↓
Compare results
```

You can compare:

```text
Model V1 vs Model V2
Prompt V1 vs Prompt V2
Policy V1 vs Policy V2
Classifier V1 vs Classifier V2
```

against exactly the same initial state.

---

# 9. Replay

Separate Replay from Fork.

### Replay

```text
Checkpoint C
    ↓
Replay
    ↓
same workflow
```

without changing the original execution.

Example:

```text
Trade TRD-1001
      ↓
Validation
      ↓
Counterparty enrichment
      ↓
SSI lookup
      ↓
Prematch
```

Replay it to verify that:

```text
same input
same checkpoint
same workflow
```

produces the expected result.

Replay is useful for:

- Agent reliability testing
- Regression testing
- Debugging
- Model upgrades
- Policy upgrades
- Agent evaluation

---

# 10. Replay vs Fork vs Time Travel

| Capability | Purpose |
|---|---|
| **Replay** | Re-run an existing execution |
| **Time Travel** | Go back to an earlier checkpoint |
| **Fork** | Create an alternate execution from a checkpoint |
| **Update State** | Change state at a checkpoint |
| **Resume** | Continue interrupted execution |
| **Fault Recovery** | Continue after failure |

Conceptually:

```text
                 A
                 │
                 B
                 │
                 C
                 │
                 D
```

### Replay

```text
A → B → C → D
       ↻
```

### Time Travel

```text
A → B → C → D
    ↑
    │
  go back
```

### Fork

```text
             B
            / \
           C   C'
           |   |
           D   D'
```

### Backtesting

```text
             Historical B
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
      Model A   Model B   Model C
        ↓         ↓         ↓
      Result    Result    Result
```

---

# 11. Get State

This should be a mandatory smoke test.

After important nodes:

```python
snapshot = graph.get_state(config)
```

Validate:

```text
snapshot.values
snapshot.next
snapshot.config
snapshot.metadata
snapshot.created_at
```

Trade example:

```python
assert snapshot.values["trade_id"] == "TRD-1001"
assert snapshot.values["trade_status"] == "EXECUTED"
```

KYC example:

```python
assert snapshot.values["document_type"] == "PASSPORT"
assert snapshot.values["passport_number"] is not None
```

---

# 12. Get State History

This is optional but highly useful for debugging.

Conceptually:

```text
Thread TRD-1001

Checkpoint 1
    ↓
Checkpoint 2
    ↓
Checkpoint 3
    ↓
Checkpoint 4
    ↓
Checkpoint 5
```

Test:

```python
history = list(graph.get_state_history(config))
```

Verify:

```text
number of checkpoints
ordering
checkpoint IDs
parent relationships
state values
node metadata
timestamps
```

---

# 13. Filter State History

This is useful when a thread has hundreds or thousands of checkpoints.

Examples:

Find checkpoints created by:

```text
node = "document_classifier"
```

Find checkpoints where:

```text
document_type == "PASSPORT"
```

Find checkpoint before:

```text
2026-09-15 10:30
```

This can remain an optional persistence-query test because it is more about checkpoint inspection and query efficiency than core execution semantics.

---

# 14. Delta Channel / Incremental State

Treat this primarily as a **performance experiment**.

Compare:

### Full State

```text
Checkpoint 1 → Full State
Checkpoint 2 → Full State
Checkpoint 3 → Full State
Checkpoint 4 → Full State
```

### Delta

```text
Checkpoint 1 → Full State

Checkpoint 2 → Δ2
Checkpoint 3 → Δ3
Checkpoint 4 → Δ4
```

Measure:

```text
SQLite database size
Write latency
Read latency
Checkpoint creation latency
Recovery latency
Serialization size
CPU
Memory
```

Example test matrix:

| Test | Full State | Delta |
|---|---:|---:|
| 1K checkpoints | | |
| DB size | | |
| Avg write latency | | |
| Avg read latency | | |
| Recovery latency | | |
| Serialization size | | |

This is especially relevant if state contains:

```text
OCR results
large document metadata
tool outputs
LLM responses
trade enrichment
KYC extraction results
```

---

# 15. Saver Operations

Create a dedicated **Saver Contract Test**.

## Store

```text
State
 ↓
Checkpoint
 ↓
SQLite
```

## Fetch

```text
thread_id
 +
checkpoint_id
 ↓
checkpoint
```

## History

```text
thread_id
 ↓
checkpoint list
```

## Latest checkpoint

```text
thread_id
 ↓
latest state
```

Verify:

```text
write → read → deserialize → state equality
```

This test should ideally run without the full agent.

That separates:

```text
Agent tests
      +
Persistence tests
```

and makes persistence failures easier to isolate.

---

# 16. Serialization + Encryption

Make this a dedicated security test suite.

Persistence pipeline:

```text
Agent State
    ↓
Serialize
    ↓
Encrypt
    ↓
SQLite
```

Read pipeline:

```text
SQLite
    ↓
Decrypt
    ↓
Deserialize
    ↓
Agent State
```

## Plaintext check

After writing a checkpoint, SQLite should **not contain sensitive values** such as:

```text
PAN
Passport number
DOB
Address
Account number
Trade details
PII
```

Instead, encrypted ciphertext should be stored.

## Round-trip

```python
original_state
      ↓
serialize
      ↓
encrypt
      ↓
decrypt
      ↓
deserialize
      ↓
restored_state
```

Then:

```python
assert restored_state == original_state
```

## Tampering test

Modify encrypted checkpoint bytes:

```text
ciphertext
   ↓
tamper
   ↓
decrypt
   ↓
FAIL
```

The system should not silently produce corrupted state.

---

# 17. Checkpoint Isolation

For a banking system, make this mandatory.

Run:

```text
Thread A = TRD-1001
Thread B = TRD-1002
```

Then:

```python
state_a = graph.get_state(config_a)
state_b = graph.get_state(config_b)

assert state_a.values["trade_id"] == "TRD-1001"
assert state_b.values["trade_id"] == "TRD-1002"
```

Then attempt to access a checkpoint belonging to another thread and verify it is rejected or inaccessible.

This is important because:

**SQLite persistence + thread IDs + checkpoint IDs** can become part of the security boundary.

---

# 18. Suggested Test Suite Structure

```text
tests/
│
├── persistence/
│   ├── test_get_state.py
│   ├── test_state_history.py
│   ├── test_checkpoint.py
│   ├── test_checkpoint_isolation.py
│   ├── test_serializer.py
│   └── test_encryption.py
│
├── execution/
│   ├── test_interrupt_resume.py
│   ├── test_hitl_approve.py
│   ├── test_hitl_reject.py
│   ├── test_hitl_edit.py
│   ├── test_tool_interrupt.py
│   ├── test_tool_failure.py
│   └── test_fault_recovery.py
│
├── time_travel/
│   ├── test_time_travel.py
│   ├── test_update_state.py
│   ├── test_fork.py
│   ├── test_pending_writes.py
│   └── test_replay.py
│
├── performance/
│   ├── test_checkpoint_size.py
│   ├── test_delta_vs_full_state.py
│   ├── test_checkpoint_latency.py
│   └── test_recovery_latency.py
│
└── business/
    ├── trade_prematching/
    │   ├── test_trade_recovery.py
    │   └── test_trade_backtesting.py
    │
    └── kyc/
        ├── test_document_recovery.py
        └── test_classifier_time_travel.py
```

---

# 19. Most Important End-to-End Test

Create one **Golden Scenario** combining the major capabilities.

## KYC Example

```text
Upload Passport
      ↓
OCR
      ↓
Document Classifier
      ↓
Checkpoint C1
      ↓
Field Extraction
      ↓
Checkpoint C2
      ↓
Validation
      ↓
HITL
```

Deliberately introduce:

```text
Classifier incorrectly says:
DRIVING_LICENSE
```

Then:

1. Persist C1.
2. Continue until C2.
3. Discover classifier error.
4. Time travel/fork from C1.
5. Change `document_type = PASSPORT`.
6. Replay remaining graph.
7. Compare original and corrected executions.
8. Verify the original history is still available.

This single scenario validates a large portion of the persistence architecture.

---

# 20. Trade Prematching Golden Scenario

Equivalent Trade Prematching flow:

```text
Trade received
      ↓
Trade validation
      ↓
Counterparty enrichment
      ↓
SSI lookup
      ↓
Prematch decision
      ↓
HITL
```

Introduce:

```text
Wrong SSI
```

Then:

```text
Checkpoint
    ↓
Fork
    ↓
Correct SSI
    ↓
Replay remaining nodes
    ↓
New prematch result
```

Compare:

```text
Original result
      VS
Corrected result
```

This becomes a powerful **agent backtesting framework**.

---

# 21. Final Test Taxonomy

Present the overall initiative as five layers:

```text
┌─────────────────────────────────────────────┐
│ 5. Security                                │
│ Serialization / Encryption / Isolation     │
├─────────────────────────────────────────────┤
│ 4. Performance                              │
│ Delta / DB size / latency / throughput     │
├─────────────────────────────────────────────┤
│ 3. Temporal Execution                       │
│ Replay / Time Travel / Fork / Backtesting  │
├─────────────────────────────────────────────┤
│ 2. Reliability                              │
│ Interrupt / Resume / Failure / Recovery    │
├─────────────────────────────────────────────┤
│ 1. Persistence                              │
│ State / History / Checkpoint / Saver       │
└─────────────────────────────────────────────┘
```

Recommended overall name:

> **LangGraph Agent Short-Term Memory & Durable Execution Test Framework**

Mandatory capabilities can then be grouped into:

### Persistence
- Get State
- Checkpoint CRUD
- History

### Durable Execution
- Interrupt/Resume
- Tool interruption
- Fault recovery

### Temporal Execution
- Replay
- Time travel
- Fork
- Pending writes

### Security
- Serialization
- Encryption
- Isolation

### Performance
- Delta state
- Checkpoint size
- Read/write latency

This provides a clear way to demonstrate to banking architecture and engineering teams **why each test exists and which failure mode it protects against**.
