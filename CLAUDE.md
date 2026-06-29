# Project Rules

/caveman

## Git Commits

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[(scope)]: <description>

[optional body]

[optional footer]
```

**Allowed types:** `feat` `fix` `chore` `docs` `refactor` `test` `ci` `perf` `style` `build` `revert`

**Scope:** optional. When used, lowercase, noun: `feat(auth):`, `fix(api):`.

**Breaking changes:** footer only — `BREAKING CHANGE: <description>`. Never use `!` suffix.

**Rules:**
- Description: imperative mood, lowercase, no period — `add user login` not `Added user login.`
- Subject line ≤ 72 chars
- Body: wrap at 72 chars, explain *why* not *what*
- One logical change per commit
