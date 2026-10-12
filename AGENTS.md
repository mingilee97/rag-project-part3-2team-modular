# Minimal RAG scaffold

- Read README.md and docs/handoff.md before editing.
- This repository starts with interfaces and empty stage folders only. Do not import the existing RAG implementation unless the user requests it.
- Keep user-facing documentation and code comments in Korean. Keep agent instructions in English.
- Implement one stage per branch and pull request. Preserve the shared contracts or document breaking changes.
- Never commit source RFP documents, extracted text, embeddings, indexes, model weights, credentials, private evaluation records, or runtime logs.
- Use synthetic inputs for offline validation. Do not call paid APIs or download models for routine checks.
- Run `python -m unittest discover -s tests` and `git diff --check` after code changes.
- Keep unimplemented stages explicitly marked. Do not return fabricated answers or claim end-to-end RAG support.
