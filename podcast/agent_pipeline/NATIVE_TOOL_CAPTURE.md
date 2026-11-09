# Native worker tool capture

The actual worker may act as capture driver. Record its actual collaboration ID
separately from the job's role agent ID. This avoids asking the root to repeat
opens. The root can inspect original receipts; this is not cryptographic proof
that a remote connector ran, and the bridge never claims automatic attestation.

Use an existing verified owner-private receipt directory, outside GitHub. Do not
send private data in URLs. One exact public URL per call keeps provenance clear.
Discover the connector tool if its name differs. Execute the following in
`functions.exec` (not Node or a Python subprocess pretending to call tools).

```js
const requestedURL = "https://www.nea.gov.sg/corporate-functions/weather";
const started_at = new Date().toISOString();
const original = await tools.mcp__codex_apps__chat_search_web_run({
  open: [{ref_id: requestedURL, lineno: null}], response_length: "long"
});
const observed_at = new Date().toISOString();
const envelope = {request_url: requestedURL, started_at, observed_at, tool_result: original};
// The entire returned JSON is retained, not a paraphrase or invented transcript.
// JSON.stringify twice makes data a safely quoted Python string, not source.
const dataLiteral = JSON.stringify(JSON.stringify(envelope));
const py = "import json\nfrom podcast.agent_pipeline.native_capture import save_receipt\n" +
  "data=json.loads(" + dataLiteral + ")\n" +
  "print(json.dumps(save_receipt('/ABSOLUTE/VERIFIED/PRIVATE/RECEIPTS',data)))\n";
const saved = await tools.exec_command({
  cmd: "/workspace/scratch/084eb96a28b1/brief-cloud-venv/bin/python -B - <<'CAPTURE_PY'\n" + py + "CAPTURE_PY\n",
  workdir: "/workspace/scratch/084eb96a28b1/brief-cloud-runner",
  sandbox_permissions: "require_escalated",
  justification: "May I preserve this actual public tool result in the authorized private receipt directory?"
});
text(saved);
text(original); // Inspect actual ref/outcome; never invent a successful page open.
```

The quoted heredoc contains generated fixed Python plus a single escaped JSON
string. Do not interpolate raw website text into commands. If persistence fails,
keep the original result in working context and retry only receipt saving, not
another tool call disguised as the first.

After reviewing the response, use its actual returned reference and explicit
outcome. Failed/unclear opens must use `failed`/`unknown`; those retain measured attempt evidence but cannot be promoted
to successful source access. Search discovery is not an open receipt.

```
python -m podcast.agent_pipeline.native_capture --directory PRIVATE_RECEIPTS manifest \
  --receipt-id RECEIPT_HASH --driver-id ACTUAL_CAPTURE_WORKER_ID \
  --tool-ref ACTUAL_RETURNED_REF --outcome opened
```

Save that generated manifest privately, then submit through
`native_bridge ... ingest_evidence --job-id ... --request-hash ... --agent-id ROLE_AGENT_ID --manifest-file ...`.
The original result's canonical JSON SHA256, actual wrapper start/end, reference,
public requested URL and capture-driver ID are preserved. Only wrapper timing is
measured; it is not the remote server's execution time. The driver's reviewed
outcome remains an attributed assertion. No raw tool content enters AuditStore.
