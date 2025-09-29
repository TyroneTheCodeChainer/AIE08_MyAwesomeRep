# Branch Development Rule

You always prefer to use branch development. Before writing any code - you create a feature branch to hold those changes. 

After you are done - provide instructions in a "MERGE.md" file that explains how to merge the changes back to main with both a GitHub PR route and a GitHub CLI route.

## Implementation Guidelines

1. **Always create feature branches**: Before making any changes, create a descriptive feature branch
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Make focused commits**: Each commit should represent a logical unit of work

3. **Provide merge instructions**: Always include a MERGE.md file with:
   - Summary of changes
   - Files modified/added
   - GitHub PR merge instructions
   - GitHub CLI merge instructions
   - Verification steps

4. **Code review ready**: Ensure all changes are well-documented and tested before requesting merge
