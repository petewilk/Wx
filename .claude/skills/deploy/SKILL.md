---
name: deploy
description: Deploy the Wx HTML apps to petewilk.com by running ./deploy.sh. Use when the user says "deploy", "publish", "push to the site", or invokes /deploy.
---

# Deploy Wx to petewilk.com

`./deploy.sh` rsyncs the git-tracked top-level `*.html` files to `dreamhost:petewilk.com/`. It refuses to run unless `main` is checked out. The remote web root also holds WordPress — never run rsync against it by hand or with `--delete`.

1. Run `git status --short` and `git branch --show-current`.
   - Not on `main`: stop and tell the user. Don't switch branches or merge unless they ask.
   - Uncommitted or untracked `*.html` files: list them and note they won't be deployed (or that the committed version will be).
   - `main` behind or ahead of `origin/main`: mention it.
2. Run `./deploy.sh -n` and show the user the file list.
3. Run `./deploy.sh`, then report which files were uploaded and the commit hash.
4. If SSH fails, report the error verbatim; key auth uses the `dreamhost` alias in `~/.ssh/config`.
