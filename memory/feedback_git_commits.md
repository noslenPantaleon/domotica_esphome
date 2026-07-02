---
name: feedback-git-commits
description: User handles all git commits themselves — never run git commit
metadata:
  type: feedback
---

Never run `git commit` on behalf of the user. The user commits each step manually.

**Why:** User prefers full control over commit history and messages.

**How to apply:** After completing each implementation step, stop and let the user commit. Do not stage or commit files.
