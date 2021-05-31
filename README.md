## Configuration Prerequisites

To use jitab you need three things:
- a gitlab token with `api` permissions (issue one here https://gitlab.com/profile/personal_access_tokens)
- a jira token (issue one here https://id.atlassian.com/manage-profile/security/api-tokens)
- a Json configuration file called `.jitab` in your home:

```json
{
    "gitlab": {
        "token": <gitlab-token>,
        "username": <gitlab-username>
    },
    "jira": {
        "token": <jira-token>,
        "username": <jira-username>
    }
}
```

## Board Prerequisites

Jitab works with both kanban and scrum workflows, but on jira there's a third board type (`simple`) which screws things up.

A `simple` board can be both... And its purpose is to help people setting up boards fast. 

Jitab treats by default `kanban` and `simple` the same way, but if you're using `scrum` workflow and your team's board is `simple`, then jitab won't work.

In future releases we may fix this problem or simply ask to change your board type to a proper scrum.

## Configuration

Once you fulfilled all the requirements, start using jitab by configuring it.

Run `jitab config` and follow the questions you'll be asked. You should run this command only once (or if you change the board).

Your global `.jitab` will be updated.

## Project init

Every project you want to use jitab with should be initialized.

Run `jitab init` to do it. This will create a local `.jitab` file with project information.
For example:
```json
{
    "id": 12345678,
    "name": "Jitab",
    "description": "",
    "path": "jitab"
}
```

## Working on tasks

Jitab will read issues from jira and will create a local git branch according to the jira task title.

Commands involved in this process are:
- `jitab new` picks tasks from your to-do columns
- `jitab wip` picks tasks from your wip columns

Branches will follow this naming convention (i.e. `feature/TEST-12-your-branch-title`).

## Pushing changes

Jitab supports `git commit` and will prefix the message with the jira key (i.e. `TEST-12: awesome message`).

Run `jitab commit -m 'awesome message'`

## Creating merge request

Once you're happy with your changes, you can create the merge request issuing `jitab mr`.
