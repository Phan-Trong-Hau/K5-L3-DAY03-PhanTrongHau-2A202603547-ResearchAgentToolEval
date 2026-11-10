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

