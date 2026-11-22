# Publication Audit

**Audit date:** 2026-11-22

**Scope:** Public GitHub repository readiness review

## Purpose of this audit

This audit reviewed the project for common publication risks before sharing it through a public GitHub repository. The review focused on sensitive information, repository hygiene, dependency declarations, setup documentation, data handling, and known project limitations.

The audit was read-only. Project code and tests were not executed, and no remote repository settings were changed.

Finding no exposed secrets does not prove that the repository is completely safe. The results describe only what was checked during this review.

## What was checked

- Git status and synchronization state
- Files tracked by Git
- Untracked and ignored local files
- Current tracked content and Git history for high-confidence secret patterns
- Potential credentials, private keys, tokens, environment files, and database files
- Git commit metadata for potentially identifying information
- `.gitignore` coverage
- Python imports and declared dependencies
- Streamlit configuration
- Runtime and development requirements
- README setup instructions
- README coverage of:
  - purpose;
  - data collection;
  - data persistence;
  - user interaction;
  - setup;
  - learning;
  - limitations and external assistance.

## Checks that passed

- The working tree was clean and synchronized with the remote `main` branch at the time of the audit.
- No high-confidence API keys, access tokens, private keys, or credentials were detected in current tracked files.
- No high-confidence secret patterns were detected in the available Git history.
- No environment files, secret configuration files, databases, dependency folders, caches, or generated files were tracked.
- Local virtual environments, Python caches, pytest caches, compiled Python files, and `.DS_Store` files were excluded by Git.
- `.streamlit/secrets.toml` was excluded by Git.
- The tracked Streamlit configuration contained theme and server settings but no secrets.
- Runtime and development requirements files were present.
- The README contained all documentation sections required by the assignment.
- The README described the TVMaze data source, API requests, JSON responses, temporary storage, user workflow, setup, learning outcomes, limitations, and external assistance.
- The application does not require an API key for the documented TVMaze endpoints.

## Initial confirmed issues

### 1. Directly imported dependency not explicitly declared

`tvmaze_api.py` imports `urllib3` directly, but `urllib3` is not explicitly listed in `requirements.txt`. It is currently available as an indirect dependency of Requests, but direct imports should normally be declared directly.

**Recommended resolution:** add an appropriate `urllib3` version range to `requirements.txt`, then verify installation and tests in a clean virtual environment.

### 2. Environment files are not covered by `.gitignore`

No `.env` file was found or tracked, but `.gitignore` does not currently protect possible future files such as `.env` or `.env.local`.

**Recommended resolution:** add rules for `.env` and `.env.*`, while allowing a sanitized `.env.example` if one is ever needed.

### 3. Commit metadata contains an author email

Git history contains an author email that is not a GitHub-provided `noreply` address. The address is intentionally not reproduced in this audit.

**Recommended resolution:** use a GitHub `noreply` address for future commits if the author does not want a personal email exposed. Rewriting existing public history is disruptive and should only be considered if removing the existing metadata is important.

## Possible concerns requiring a decision

### Named classroom assistance

The README names a person who assisted with understanding API connections. This appears intentional, but it is still personally identifying information about another person.

**Recommended resolution:** confirm that the person is comfortable being named publicly. Otherwise, replace the name with a general description such as “my course instructor.”

### Project source-code license

The README credits TVMaze and discusses its data licensing, but the repository does not contain a separate license for the project's own source code.

**Recommended resolution:** add a `LICENSE` file if other people should be allowed to reuse or modify the code. Keep the source-code license separate from TVMaze's data and image terms.

### TVMaze attribution

The README includes TVMaze attribution and refers to CC BY-SA licensing. The exact current wording and license version were not independently verified during this offline audit.

**Recommended resolution:** compare the final attribution with the current official TVMaze licensing documentation before submission.

## Fixes made

- A sanitized `AUDIT.md` was added to document the publication review.
- `urllib3>=2,<3` was added to `requirements.txt` because the package is imported directly by the API client.
- `.env` and `.env.*` were added to `.gitignore`.
- `!.env.example` was added so a future sanitized configuration example can still be committed.
- The repository's future Git author email was configured to use the GitHub `noreply` address.
- Existing commits on `main` were rewritten so their author and committer metadata use the GitHub `noreply` address instead of the previous personal address.
- Dependencies were installed in a newly created clean virtual environment.
- The complete automated test suite passed in that clean environment: 6 tests passed.
- The temporary verification environment was removed after the test.

No application behavior was changed by these publication fixes.

## Recommended repository improvements

- Consider ignoring coverage output, IDE settings, and build directories if those tools are used later.
- Consider documenting the exact Python version used for final testing.
- Consider providing a dependency lock or frozen dependency snapshot for reproducible installations.
- Recheck TVMaze's current attribution and licensing wording before final submission.

## Remaining project limitations

- The project focuses on television series rather than a complete film catalogue.
- Recommendations are created from ratings and genres across selected TVMaze catalogue pages; they are not personalized recommendations.
- The watchlist and recently viewed list exist only for the current Streamlit session.
- There is no database, login system, user account, or synchronization between devices.
- The application depends on an internet connection and the continued availability of TVMaze.
- Some TVMaze records may have missing posters, summaries, dates, or ratings.
- Long-running shows can create a large episode page when all seasons are displayed.
- The application does not stream or host video content.

## Items not verified

Because project code was not executed during the audit, the following were not verified:

- Installation in a new, empty virtual environment
- Successful dependency resolution on a clean machine
- Application startup and interactive behavior
- Automated test results
- Live TVMaze response compatibility
- Runtime behavior during network failures or rate limiting
- Current third-party dependency vulnerabilities
- Current TVMaze licensing requirements
- Remote repository visibility, permissions, and branch-protection settings

## Decisions on initial possible concerns

### Named classroom assistance

The project owner confirmed that naming Ricardo in the README is acceptable. The attribution remains in the documentation.

### Project source-code license

The project owner decided not to add a source-code license because this is an educational class project. This means the repository does not grant a general open-source reuse license. TVMaze's separate terms continue to apply to the television data and images supplied by TVMaze.

### TVMaze attribution

The README continues to credit TVMaze and identify the project as educational. Verifying the latest wording against TVMaze's current official licensing terms remains recommended before final submission.

## Second audit after remediation

**Second audit date:** 2026-11-22

The second audit reviewed the repository again after applying the requested fixes.

### Second-audit results

- No high-confidence secrets, access tokens, API keys, or private-key patterns were detected in the project files reviewed.
- `urllib3` is now explicitly declared with the range `>=2,<3`.
- A fresh virtual environment successfully installed all runtime and development dependencies.
- The automated tests passed in the fresh environment: 6 tests passed.
- `.env` and environment-specific variants such as `.env.local` are now ignored.
- A sanitized `.env.example` remains eligible to be committed in the future.
- All author and committer email addresses in the rewritten local `main` history use the GitHub `noreply` domain.
- The README still contains all seven required assignment sections.
- The tracked Streamlit configuration contains no secret values.
- No whitespace errors were found in the pending publication changes.
- Ricardo's attribution was reviewed and intentionally retained.
- The absence of a source-code license was reviewed and accepted as an intentional decision for this educational project.

### Remaining limitations after the second audit

- Secret-pattern scanning cannot guarantee that no sensitive information exists.
- Current third-party dependency vulnerabilities were not assessed with a dedicated vulnerability database or scanner.
- Live TVMaze endpoints and current licensing terms were not independently revalidated during the second audit.
- GitHub repository visibility, permissions, branch protection, and cached unreachable Git objects could not be verified from the local repository.
- Rewriting the visible branch history removes the previous email from current commit metadata, but hosting platforms may retain unreachable objects or caches according to their own retention policies.

## Publication status

The confirmed dependency and ignore-rule issues were fixed, a clean installation and test run succeeded, and the visible local `main` history now uses privacy-preserving GitHub `noreply` metadata. No confirmed exposed secrets were found in the reviewed files. Publication is considered ready subject to the remaining limitations documented above and successful synchronization of the rewritten branch with the remote repository.
