# JSON for Modern C++ Release Scripts

## Preparations

- Install required tools: `make install_requirements`.
- Add required keys to `config.json` (apparently not checked in to GitHub).

## Release Checklist

1. Set the version number.

   - [ ] Edit file `config.json`.

2. Check if the milestone is correctly set.

   - [ ] Check <https://github.com/nlohmann/json/milestones>: Are all assigned issues closed? Is the due date set to today?

3. Clean the working directory.

   - [ ] Execute `rm -fr workdir/json`.

4. Update feature slideshow.

   - [ ] Adjust version and content in slideshow `scripts/slideshow/JSON.key`.

5. Checkout working copy and bump versions.

   - [ ] Execute `make pass_1`.

6. Make last adjustments to the working copy `workdir/json`.

   - [ ] Edit `README.md` and add new contributors.

7. Commit all changes to the working copy.

   - [ ] Execute `make pass_2`.

8. Create an empty release draft and push it to GitHub.

   - [ ] Execute `make pass_3`.

9. Edit the created release draft.

   - [ ] Go to <https://github.com/nlohmann/json/releases> and add the release notes based on WIP discussion post.

10. Wait for the CI to complete on the pushed release branch.

   - [ ] Wait until <https://github.com/nlohmann/json/actions> is green.

11. Merge the release branch and push all changes.

   - [ ] Execute `make pass_4`.

12. Publish the release.

   - [ ] Go to <https://github.com/nlohmann/json/releases> and publish the release. Remember to tick the "Create a discussion for this release" checkbox.

13. Create PR for Homebrew formula.

   - [ ] Execute `make update_homebrew`.

14. Clean up discussions.

   - [ ] Unpin posts.
   - [ ] Close WIP post.
   - [ ] Create WIP post for next release.
   - [ ] Pin post for current release.

15. Close current and create a new milestone.

   - [ ] Go to <https://github.com/nlohmann/json/milestones>.
