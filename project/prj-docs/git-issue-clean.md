(base) avannala@Q2HWTCX6H4 spf-converter % git checkout origin/v11-fixing-refrator-issues
Already on 'origin/v11-fixing-refrator-issues'
(base) avannala@Q2HWTCX6H4 spf-converter %
(base) avannala@Q2HWTCX6H4 spf-converter %
(base) avannala@Q2HWTCX6H4 spf-converter % git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch spf-converter.tar.gz' \
  --tag-name-filter cat -- --all
WARNING: git-filter-branch has a glut of gotchas generating mangled history
	 rewrites.  Hit Ctrl-C before proceeding to abort, then use an
	 alternative filtering tool such as 'git filter-repo'
	 (https://github.com/newren/git-filter-repo/) instead.  See the
	 filter-branch manual page for more details; to squelch this warning,
	 set FILTER_BRANCH_SQUELCH_WARNING=1.
Proceeding with filter-branch...

Rewrite 027d6156b674cf9e61c824a3031796262414a825 (239/244) (20 seconds passed, remaining 0 predicted)    rm 'spf-converter.tar.gz'
Rewrite 030dc277aaef4efe84942c02c49e3b1ed3660d4c (239/244) (20 seconds passed, remaining 0 predicted)
WARNING: Ref 'refs/heads/feature-v2' is unchanged
WARNING: Ref 'refs/heads/feature-v3' is unchanged
WARNING: Ref 'refs/heads/master' is unchanged
Ref 'refs/heads/origin/v11-fixing-refrator-issues' was rewritten
WARNING: Ref 'refs/heads/v10-fixing-refrator-issues' is unchanged
Ref 'refs/heads/v4-updaates' was rewritten
WARNING: Ref 'refs/heads/v5-updates' is unchanged
WARNING: Ref 'refs/heads/v6-updates' is unchanged
WARNING: Ref 'refs/heads/v7-refactor-feature' is unchanged
WARNING: Ref 'refs/heads/v7-updates' is unchanged
WARNING: Ref 'refs/heads/v8-datamigration' is unchanged
WARNING: Ref 'refs/heads/v9-refactordb-updates' is unchanged
WARNING: Ref 'refs/remotes/origin/master' is unchanged
WARNING: Ref 'refs/remotes/origin/feature' is unchanged
WARNING: Ref 'refs/remotes/origin/feature-add-verifier' is unchanged
WARNING: Ref 'refs/remotes/origin/feature-v2' is unchanged
WARNING: Ref 'refs/remotes/origin/feature-v3' is unchanged
WARNING: Ref 'refs/remotes/origin/master' is unchanged
WARNING: Ref 'refs/remotes/origin/v10-fixing-refrator-issues' is unchanged
Ref 'refs/remotes/origin/v4-updaates' was rewritten
WARNING: Ref 'refs/remotes/origin/v5-updates' is unchanged
WARNING: Ref 'refs/remotes/origin/v6-updates' is unchanged
WARNING: Ref 'refs/remotes/origin/v7-refactor-feature' is unchanged
WARNING: Ref 'refs/remotes/origin/v8-datamigration' is unchanged
WARNING: Ref 'refs/remotes/origin/v9-refactordb-updates' is unchanged
WARNING: Ref 'refs/stash' is unchanged
WARNING: Ref 'refs/tags/v1' is unchanged
WARNING: Ref 'refs/tags/v2' is unchanged
WARNING: Ref 'refs/tags/v3' is unchanged
WARNING: Ref 'refs/tags/v4' is unchanged
WARNING: Ref 'refs/tags/v5' is unchanged
v1 -> v1 (fa272a1b3ee8ae1a61cfbbf22a2e3627f3cfed7c -> fa272a1b3ee8ae1a61cfbbf22a2e3627f3cfed7c)
v2 -> v2 (29339825eb9a4c6cd0d56d0f0d6c0c553efb0393 -> 29339825eb9a4c6cd0d56d0f0d6c0c553efb0393)
v3 -> v3 (16c953c990f6cc537f1f198b2aa93d4d7518ad59 -> 16c953c990f6cc537f1f198b2aa93d4d7518ad59)
v4 -> v4 (e591b2d4975bf033e705593fa885fb41084d6c30 -> e591b2d4975bf033e705593fa885fb41084d6c30)
v5 -> v5 (830d61f4566534ef4c997101c7feac55454ed2d2 -> 830d61f4566534ef4c997101c7feac55454ed2d2)
(base) avannala@Q2HWTCX6H4 spf-converter % git status
On branch origin/v11-fixing-refrator-issues
nothing to commit, working tree clean
(base) avannala@Q2HWTCX6H4 spf-converter % rm -rf .git/refs/original/
(base) avannala@Q2HWTCX6H4 spf-converter % git reflog expire --expire=now --all
git gc --prune=now
Enumerating objects: 1183, done.
Counting objects: 100% (1183/1183), done.
Delta compression using up to 10 threads
Compressing objects: 100% (1030/1030), done.
Writing objects: 100% (1183/1183), done.
Total 1183 (delta 747), reused 243 (delta 142), pack-reused 0
(base) avannala@Q2HWTCX6H4 spf-converter % git push origin origin/v11-fixing-refrator-issues --force
Enumerating objects: 42, done.
Counting objects: 100% (42/42), done.
Delta compression using up to 10 threads
Compressing objects: 100% (19/19), done.
Writing objects: 100% (27/27), 28.47 KiB | 28.47 MiB/s, done.
Total 27 (delta 14), reused 20 (delta 7), pack-reused 0
remote: Resolving deltas: 100% (14/14), completed with 11 local objects.
remote:
remote: Create a pull request for 'origin/v11-fixing-refrator-issues' on GitHub by visiting:
remote:      https://github.com/akv-dev/spf-converter/pull/new/origin/v11-fixing-refrator-issues
remote:
To https://github.com/akv-dev/spf-converter
 * [new branch]      origin/v11-fixing-refrator-issues -> origin/v11-fixing-refrator-issues
(base) avannala@Q2HWTCX6H4 spf-converter % git status
On branch origin/v11-fixing-refrator-issues
nothing to commit, working tree clean
(base) avannala@Q2HWTCX6H4 spf-converter %
(base) avannala@Q2HWTCX6H4 spf-converter % git checkout -b v1-mvp-release
Switched to a new branch 'v1-mvp-release'
(base) avannala@Q2HWTCX6H4 spf-converter % git add .
(base) avannala@Q2HWTCX6H4 spf-converter %
(base) avannala@Q2HWTCX6H4 spf-converter %
(base) avannala@Q2HWTCX6H4 spf-converter % git commit -m "v1-mvp-release"
On branch v1-mvp-release
nothing to commit, working tree clean
(base) avannala@Q2HWTCX6H4 spf-converter % git push --set-upstream origin v1-mvp-release
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
remote:
remote: Create a pull request for 'v1-mvp-release' on GitHub by visiting:
remote:      https://github.com/akv-dev/spf-converter/pull/new/v1-mvp-release
remote:
To https://github.com/akv-dev/spf-converter
 * [new branch]      v1-mvp-release -> v1-mvp-release
branch 'v1-mvp-release' set up to track 'origin/v1-mvp-release'.
(base) avannala@Q2HWTCX6H4 spf-converter %
(base) avannala@Q2HWTCX6H4 spf-converter %