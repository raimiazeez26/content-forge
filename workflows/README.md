# n8n workflows

Workflow JSON exports are not yet included in this repository. The test prompt
pack refers to Workflow 07 (Batch Controller), which must be exported from the
original n8n instance before those batch requests can run.

When adding exports, remove credential references, personal data, execution data,
and pinned payloads containing secrets. Configure credentials in the destination
n8n instance after importing. Do not commit credential exports.

The renderer is usable independently through its HTTP API. From n8n in this
repository's Docker Compose network, use `http://contentforge-renderer:8000`.
