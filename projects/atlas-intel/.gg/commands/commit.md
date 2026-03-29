---
name: commit
description: Run checks, commit with AI message, and push
---

1. Run quality checks — fix ALL errors before continuing:
   ```bash
   npm run typecheck 2>&1
   npm run lint 2>&1
   ```
   If errors exist, run `npm run lint:fix` first, then fix remaining manually.

2. Review changes: run `git status`, `git diff --staged`, and `git diff`.

3. Stage relevant files with `git add` (specific files, not `-A`).

4. Generate a commit message:
   - Start with a verb (Add/Update/Fix/Remove/Refactor)
   - Be specific and concise, one line preferred

5. Commit and push:
   ```bash
   git commit -m "your generated message"
   git push
   ```
