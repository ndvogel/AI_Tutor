---
description: Orchestrates a full feature/fix cycle - branch, research, build, test, validate, document, PR, merge, sync - stopping for human approval at each gate defined in CLAUDE.md.
argument-hint: [short description of the feature or fix]
allowed-tools: Bash(git:*), Bash(gh:*), Agent(researcher, builder, edge-case-writer, validator, scribe)
---

You are the orchestrator for this feature cycle. Follow CLAUDE.md's approval
gates exactly — do not skip a gate to save time.

Task: $ARGUMENTS

## Steps

1. **Create the branch.** Run `git status` to confirm the working tree is
   clean, then create and check out a new branch named
   `feature/<short-slug-of-the-task>` (or `fix/<short-slug>` if this is a
   bugfix) off the current default branch.

2. **Research.** Delegate to the `researcher` subagent with the task
   description. Wait for its report.

3. **Gate 1 — Plan approval.** Show the human the Researcher's report plus a
   short plan (2-4 sentences: what you're about to build and how). Stop and
   wait for explicit approval before continuing. If the human says this is a
   small/low-risk change and they want to skip this gate going forward,
   note that back to them but still get a yes/no on *this* task.

4. **Build.** Once approved, delegate to the `builder` subagent with the
   task description and the Researcher's report.

5. **Write tests.** Delegate to the `edge-case-writer` subagent with a
   summary of what the Builder changed.

6. **Validate.** Delegate to the `validator` subagent to run the full suite.

7. **Gate 2 — Validator report review.** Show the human the Validator's
   report in full, PASS/FAIL front and center. If it's a FAIL:
   - Do not attempt a fix yourself and do not loop back to the Builder
     automatically. Report the failure and ask the human whether to send it
     back to the Builder, adjust the approach, or stop here.

8. **Document.** Once the Validator passes, delegate to the `scribe`
   subagent, handing it the Researcher's, Builder's, Edge-Case Writer's, and
   Validator's reports. It returns a commit message, a CHANGELOG.md entry,
   and a PR title/description.

9. **Gate 3 — Commit, PR, and merge approval.** Show the human all three
   things Scribe wrote, together, in one message. Ask explicitly: "Approve
   this commit message, changelog entry, and PR description, and merge
   `<branch>` into `<default branch>`?" Wait for a clear yes. If the human
   wants wording changed, send it back to Scribe rather than editing it
   yourself.

10. **Commit, push, and open the PR.** On approval:
    - Commit the changes using Scribe's commit message.
    - Append Scribe's entry to `CHANGELOG.md` and commit that too (or amend
      into the same commit).
    - Push the branch to the remote: `git push -u origin <branch>`.
    - Open a real PR with `gh pr create --title "<title>" --body "<Scribe's
      PR description>"`. If `gh` isn't installed or isn't authenticated,
      stop here and tell the human exactly what's missing rather than
      guessing.
    - Report the PR URL to the human.

11. **Merge the PR and sync.** Ask once more: "The PR is open at <url> —
    merge it now?" (This can be the same yes as step 9 if the human already
    said "merge" there — don't make them approve twice for one decision,
    but do show them the live PR URL before it happens.) On yes:
    - Merge via `gh pr merge <branch> --merge` (or `--squash` if the human
      prefers a single clean commit — ask once, then remember their answer
      for future runs).
    - Pull the updated default branch locally: `git checkout <default
      branch> && git pull`.
    - Re-run the full test suite against the synced result via the
      `validator` subagent to confirm nothing broke in the merge.
    - Delete the feature branch, locally and on the remote, only after
      confirming the merge succeeded and the human doesn't want to keep it.
    - Report the final result.

## Rules

- Never skip Gate 2, Gate 3, or the PR-merge confirmation in step 11,
  regardless of how small the change seems.
- Never commit directly to the default branch outside of step 11.
- Never push or open/merge a PR without the human having seen the exact
  commit message and PR description first (Gate 3) — no silent wording
  changes after approval.
- If any subagent's report contradicts another (e.g. Builder says done,
  Validator finds failures), surface the contradiction to the human rather
  than silently picking one.
- If `gh` commands fail (auth, missing CLI, network), report the exact
  error rather than retrying blindly or falling back to a workaround the
  human didn't approve.
