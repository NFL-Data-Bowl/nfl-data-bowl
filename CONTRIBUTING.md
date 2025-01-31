# Repository Contribution Guide

Welcome to the repository! This document provides step-by-step instructions for pushing code to the breach protection rules.

## Prerequisites

Before pushing any code, ensure you have the following:

* Proper authentication (SSH key or Personal Access Token)

* Required branch permissions

* Latest version of Git installed

* Assigned permissions in the repository

## Steps to Push Code

### 1. Clone the Repository
```bash
# Clone the repo if you haven’t already

# HTTPS
git clone https://github.com/NFL-Data-Bowl/nfl-data-bowl.git
# SSH
git clone git@github.com:NFL-Data-Bowl/nfl-data-bowl.git
cd nfl-data-bowl
```

### 2. Create a New Branch
```bash
# Ensure you're on the latest main branch
git checkout main
git pull origin main

# Create a new feature branch
git checkout -b feature-branch-name
```

### 3. Make and Commit Changes
```bash
# Stage and commit your changes
git add .
git commit -m "Your commit message"
```

### 4. Push to Remote Repository
```bash
# Push your branch
git push origin feature-branch-name
```

### 5. Open a Pull Request (PR)

* Navigate to the repository on GitHub.

* Open a Pull Request (PR) from your branch to main.

* At least one approval is required before merging.

* Follow the required approval process before merging.

### 6. Merge the PR (If Approved)

Once your PR is approved:
```bash
git checkout main
git pull origin main
```


## Troubleshooting

- **Permission Denied?** Ensure you have the correct access.

- **Push Rejected?** Check for breach protection rules and resolve any flagged issues.

- **Approval Required?** Request a review from a teammate.

For any further issues, reach out to the repo maintainers.

----

### **For Internal Team Use Only**