# Integration Quickstart (EVM v2.1)

EVM is a lightweight, non-intrusive side-module. It does not modify model weights and must not block response generation.

## Minimal pipeline

1) on_user_message_received
- Extract entry endpoint: entry_endpoint = [X,Y,Z,G,E], and W in [0..100]

2) Generate response
- EVM SHALL NOT interfere.

3) on_model_response_generated
- Extract exit endpoint: exit_endpoint = [X,Y,Z,G,E], and W

4) Identity update
- PEV update from entry endpoint
- EEV update from exit endpoint
- Enforce FEV bounds on EEV
- Apply boundary recovery if needed

5) Append EV record
- Append-only, exactly one EV per interaction

6) Export CIS snapshots (optional but recommended)
- Use CIS for portability and audit

## Outputs
- EV Log (append-only)
- Optional Snapshot Log (reconstructable)
- Optional Index Log
