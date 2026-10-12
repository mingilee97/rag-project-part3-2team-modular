# Minimal RAG scaffold

- Read README.md and docs/handoff.md before editing.
- This repository starts with interfaces and empty stage folders only. Do not import the existing RAG implementation unless the user requests it.
- Keep user-facing documentation and code comments in Korean. Keep agent instructions in English.
- Implement one stage per branch and pull request. Preserve the shared contracts or document breaking changes.
- Read CONTRIBUTING.md and docs/modules.md. Start each task from current main; use feature/<github-id>/<stage>-<task>, fix/<github-id>/<task>, or docs/<github-id>/<task>.
- Never push directly to main or bypass its review and status requirements. Use a draft PR until the work is ready; do not self-approve.
- Do not assign module ownership or change teammates' branches without authorization. Starter branches have no assigned module.
- Never commit source RFP documents, extracted text, embeddings, indexes, model weights, credentials, private evaluation records, or runtime logs.
- Use synthetic inputs for offline validation. Do not call paid APIs or download models for routine checks.
- Run `python -m unittest discover -s tests` and `git diff --check` after code changes.
- Keep unimplemented stages explicitly marked. Do not return fabricated answers or claim end-to-end RAG support.
