---
name: github_repos
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, language, sort, limit]
outputs: [items]
side_effect: false
---
# github_repos

Searches public GitHub repositories via the GitHub REST API (`https://api.github.com/search/repositories`). Supports filtering by programming `language`, sorting by `stars`, `forks`, or `updated`, and limiting the number of returned repositories.

Optional `GITHUB_TOKEN` in `.env` enables authenticated requests. No token is required
for public search, but anonymous requests share the originating IP's limits. A rate-limit
response returns `error=rate_limit` with retry/reset metadata when supplied by GitHub;
the tool does not retry automatically.

