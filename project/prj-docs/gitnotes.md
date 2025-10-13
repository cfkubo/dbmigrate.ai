# Git Branching and Merging Notes

This guide provides simple instructions for switching between branches in this project to test new changes and for merging them into the main branch.

## 1. How to Switch Branches for Local Testing

You currently have two branches: `master` (the main, stable branch) and `feature` (where the documentation changes were just added). To test the changes on each branch, you can switch between them locally.

### View Current Branch
To see which branch you are currently on, run:
```sh
git branch
```
Your current branch will have an asterisk (`*`) next to it.

### Switch to the `master` Branch
To test the original state of the code before the recent changes, switch to the `master` branch:
```sh
git fetch origin
git checkout master
```

### Switch to the `feature` Branch
To test the new changes you just made, switch back to the `feature` branch:
```sh
git fetch origin
git checkout feature
```

**Important:** Before switching branches, make sure you have committed any work-in-progress changes or use `git stash` to save them temporarily.

## 2. How to Merge When Functionality Works

Once you have tested the `feature` branch and are confident that its changes should be in the main codebase, you can merge it into `master`.

### Step 1: Go to the `master` branch and make sure it's up-to-date
First, switch to the branch that you want to merge INTO (`master`).
```sh
git checkout master
```
Then, pull any potential changes from the remote repository to avoid conflicts.
```sh
git pull origin master
```

### Step 2: Merge the `feature` branch
Now, run the merge command to bring the changes FROM the `feature` branch INTO your current branch (`master`).
```sh
git merge feature
```
This will apply all the commits from the `feature` branch to the `master` branch.

### Step 3: Push the updated `master` branch
After the merge is successful, your local `master` branch is ahead of the remote one. Push the changes to GitHub.
```sh
git push origin master
```

### Step 4: (Optional) Delete the `feature` branch
Once the feature has been merged, you can delete the `feature` branch to keep your repository clean.

Delete the local branch:
```sh
git branch -d feature
```
Delete the remote branch on GitHub:
```sh
git push origin --delete feature
```
