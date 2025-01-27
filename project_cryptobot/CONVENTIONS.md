# test_technique_de

Here you'll find the rules for the naming conventions of the branches and commits.

Always launch the following command before working in your repository:


## Branches

The branch will have to identify which category of task you perform. For which issue and what exactly you are trying to do.

The global syntax is the following one:

`(feature|bugfix|hotfix|typo|test)/(no-ref|issue-XXXX)/task`

This means that for the category you can pick between:

- `feature`: if you create a new course, add a new notebook, etc.
- `bugfix`: if you fix an existing bug properly.
- `hotfix`: if you fix an existing bug but rapidly because of time constraints.
- `typo`: if you fix a typo in the courses.
- `test`: if you test something.

Then you'll have to identify the issue:

- if your issue is let's say the issue 145 and you want to develop a `feature: feature/issue-145/`...
- if your issue does not exist: `feature/no-ref/`...

Lastly you'll write the associated message to your branch:

- `feature/issue-145/creating-new-ml-course`: all the caracters must follow kebab-case so only lower letters numbers and -.

## Commits

The same logic applies to commits.

The global syntax will be the following one:

`(feat|fix|docs|style|refactor|test|chore|perf|other|typo)(optional): #(no-ref|XXXX) message`

Here I'll let you decide which type you have in your case:

- `feat`: for developing a feature.
- `fix`: for fixing a problem.
- `docs`: for documentation.
- `style`: for code formatting.
- `refactor`: for code cleaning.
- `test`: for testing.
- `chore`: for dependency updates.
- `perf`: for performance improvements.
- `other`: for everything else.
- `typo`: if you correct a course typo.

Then you can add the precision of your choice in parenthesis if you want:

- `feat(test): ...`

Then you can specify the issue of your ticket:

- `feat: #145 ...` if the issue exists.
- `feat: #no-ref ...` if the issue does not exists.

And then of course a message of size at least 1.
