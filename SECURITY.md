# Security Policy

## Scope

This policy covers the current repository contents, including the LLM build harness, the launcher under `docs/`, and generated browser-game artifacts under `docs/games/` and `generated/`.

Report suspected vulnerabilities in the current contents. Include the affected repository-relative path and revision or build identifier.

## Reporting a vulnerability

Please report potential vulnerabilities privately to a repository maintainer through an authorized private channel. Do not publish exploit details, credentials, private configuration, or proof-of-concept code in public issues, launcher metadata, or generated public output.

If no private reporting channel has been provided, request one from a maintainer without including sensitive details.

A useful report includes:

- A concise description and potential impact.
- Affected paths, revision, and relevant build identifier.
- Reproduction steps or a minimal proof of concept, shared only through the private channel.
- Relevant environment or configuration details, with secrets redacted.
- Any suggested mitigation or workaround.

## Repository-specific considerations

The active browser-game build resolves runtime and input integrations through import-map aliases and uses local fallbacks when those imports fail. Reports involving those integrations should identify the affected alias or fallback path and whether the issue occurs with the remote module, the local fallback, or both.

The repository's registered deterministic tools validate queue and state data, repository write boundaries, and selected syntax, manifest, and HTML conditions. They are not security reviews or a guarantee that generated output is secure.

## Disclosure

Please avoid public disclosure of a suspected vulnerability until maintainers have had an opportunity to assess it and coordinate a fix. This repository does not currently define a response timeline, supported-release policy, or disclosure and credit process.
