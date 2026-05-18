# Git Workflow Guide - Fintech Review Analytics

A structured Git workflow with branches, PRs, and CI/CD integration for collaborative development.

## Branch Strategy

```
main (production)
  ↑
develop (staging)
  ↑
task-1, task-2, task-3, task-4 (feature branches)
  ↑
feature/* (experimental)
```

### Branch Naming Conventions

- **main**: Production-ready code (stable, tagged releases)
- **develop**: Integration branch (all tasks merged here)
- **task-X**: Task-specific branches (Task 1-4)
- **feature/***: Feature development (feature/sentiment-model, feature/viz-engine)
- **bugfix/***: Bug fixes (bugfix/data-validation)
- **hotfix/***: Critical production fixes (hotfix/security-patch)

## Workflow: Creating & Merging a Task

### Step 1: Create Feature Branch

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch for Task 2
git checkout -b task-2

# Or create from develop
git checkout develop
git pull origin develop
git checkout -b task-2
```

### Step 2: Implement & Commit

```bash
# Make changes to code/notebooks
vim src/sentiment.py
vim notebooks/02_task2_analysis.ipynb

# Stage changes
git add src/sentiment.py notebooks/02_task2_analysis.ipynb

# Commit with descriptive message
git commit -m "feat(task-2): Implement VADER sentiment analysis with 90%+ coverage

- Add SentimentAnalyzer class with VADER integration
- Implement sentiment classification (positive/negative/neutral)
- Add per-bank aggregation and statistics
- Add 6 business themes with keyword matching
- Achieve 90%+ sentiment coverage (1,080+ reviews classified)
- Complete Task 2 notebook with 8 sections
- All KPIs validated successfully"
```

### Step 3: Push & Create Pull Request

```bash
# Push to remote
git push origin task-2

# Create PR on GitHub:
# - Title: "Task 2: Sentiment & Thematic Analysis"
# - Description: Include objectives, changes, and KPIs met
# - Assign reviewer(s)
# - Add labels: enhancement, task-2, analysis
```

### Step 4: Code Review & CI/CD

- GitHub Actions automatically runs:
  - Linting (pylint)
  - Code formatting (black, isort)
  - Unit tests (pytest)
  - Security checks (bandit)
  - Coverage reporting
- Reviewer provides feedback
- Author makes requested changes
- Re-commit and push changes

### Step 5: Merge to Develop

```bash
# After PR approval and CI passes:
# Merge via GitHub UI (Squash & Merge or Create Merge Commit)

# Or merge locally:
git checkout develop
git pull origin develop
git merge --no-ff task-2 -m "Merge task-2: Sentiment & Thematic Analysis"
git push origin develop
```

### Step 6: Integration & Testing

```bash
# Pull merged changes
git checkout develop
git pull origin develop

# Run full test suite
pytest tests/ -v

# Verify pipeline end-to-end
python run_pipeline.py
```

### Step 7: Prepare Release (Merge to Main)

```bash
# Create release branch
git checkout -b release/v1.0.0

# Update version numbers, changelog
vim VERSION.txt
git add VERSION.txt
git commit -m "chore(release): Version 1.0.0 with Tasks 1-4 complete"

# Merge to main
git checkout main
git pull origin main
git merge --no-ff release/v1.0.0 -m "Release v1.0.0"

# Tag release
git tag -a v1.0.0 -m "Production release: All tasks complete"

# Push
git push origin main
git push origin v1.0.0
```

## Commit Message Convention

Follow Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation
- **style**: Formatting, missing semicolons
- **refactor**: Code refactoring
- **perf**: Performance improvement
- **test**: Adding/updating tests
- **chore**: Build, dependencies, tooling

### Scopes

- **task-1**: Web scraping & preprocessing
- **task-2**: Sentiment & thematic analysis
- **task-3**: Visualizations & insights
- **task-4**: Database integration

### Examples

```
feat(task-2): Implement sentiment analysis with VADER

Implement SentimentAnalyzer class using VADER sentiment classification.
Add per-bank aggregation and theme detection.
Achieve 90%+ coverage on 1,200 reviews.

Fixes #42
```

```
fix(task-1): Handle missing review dates in preprocessing

Previously, reviews with missing dates were dropped entirely.
Now, missing dates are filled with review_date field if available.

Closes #23
```

## PR Checklist

Before creating PR, verify:

- [ ] Code follows PEP 8 style guide
- [ ] New functions have docstrings
- [ ] All tests pass locally: `pytest tests/`
- [ ] Code coverage > 70%: `pytest --cov=src`
- [ ] Linting passes: `pylint src/`
- [ ] No hardcoded credentials or secrets
- [ ] Commit messages are descriptive
- [ ] All KPIs for task are met
- [ ] Notebook cells execute without errors
- [ ] Documentation updated if needed

## Code Review Guidelines

### For Reviewers

- Check logic and correctness
- Verify error handling
- Ensure performance is acceptable
- Confirm documentation is clear
- Look for potential security issues
- Verify all tests pass
- Check for code duplication

### For Authors

- Address all review comments
- Ask questions if feedback unclear
- Re-request review after changes
- Keep PRs focused and reasonably sized

## CI/CD Pipeline

Automatic checks on every push/PR:

```
Push to branch
    ↓
GitHub Actions triggers
    ├─ Lint check (pylint)
    ├─ Format check (black, isort)
    ├─ Unit tests (pytest)
    ├─ Code coverage (>70%)
    ├─ Security scan (bandit)
    └─ Notebook validation
    
Result: ✓ All pass → Ready to merge
Result: ✗ Fails → Fix issues and re-push
```

## Conflict Resolution

### Resolve merge conflicts

```bash
# During merge, if conflicts occur:
git status  # See conflicting files

# Edit conflicting files manually
# Markers: <<<<<<, ======, >>>>>>

# After resolving:
git add <resolved-files>
git commit -m "chore: Resolve merge conflicts with develop"
git push origin task-2
```

## Synchronizing Branches

### Update feature branch with develop

```bash
git checkout task-2
git fetch origin
git rebase origin/develop

# If conflicts, resolve them
# Then force push
git push origin task-2 --force-with-lease
```

### Update develop from main

```bash
git checkout develop
git pull origin main
git push origin develop
```

## Release Management

### Version Tags

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0 - All tasks complete"

# Push tag
git push origin v1.0.0

# View tags
git tag -l
git show v1.0.0
```

## Useful Git Commands

```bash
# View branch history
git log --graph --oneline --all

# Show current branch
git branch -v

# Delete local branch
git branch -d task-2

# Delete remote branch
git push origin --delete task-2

# Revert last commit
git revert HEAD

# Stash changes temporarily
git stash
git stash pop

# Cherry-pick commit to another branch
git cherry-pick <commit-hash>

# Squash commits before merging
git rebase -i HEAD~3  # Interactive rebase last 3 commits
```

## GitHub Issues & Project Management

### Link commits to issues

```bash
# In commit message:
Fixes #42
Closes #123

# This automatically closes issues when PR merges
```

### Create issues

- Title: Clear, concise description
- Description: Problem, expected behavior, actual behavior
- Labels: enhancement, bug, task-1, help wanted
- Assignee: Developer responsible
- Project: Add to project board

## Continuous Integration Status

Check status at: https://github.com/Arsema6/fintech-review-analytics/actions

## Questions & Support

- Code style questions → Check PEP 8 style guide
- Git help → `git help <command>`
- Commit history questions → `git log --oneline | head -20`
