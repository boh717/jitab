import argparse
import sys
import os
import json

from typing import List
from typing_extensions import Literal

from jitab.jira.api import JiraAPI
from jitab.gitlab.api import GitlabAPI
from jitab.git.api import GitAPI

from jitab.config.service import ConfigService
from jitab.gitlab.service import RepoInitService
from jitab.jira.service import JiraService

from jitab.config.model import Configuration
from jitab.gitlab.model import Repository
from jitab.jira.model import Issue

TicketType = Literal["new", "wip"]

def run():
    parser = argparse.ArgumentParser(prog='jitab')

    subparsers = parser.add_subparsers()

    parser.set_defaults(func=lambda: parser.print_usage())

    parser_config_jira = subparsers.add_parser('config', help='Run this command the first time you run jitab to configure board and input/output columns')
    parser_config_jira.set_defaults(func=config)

    parser_init = subparsers.add_parser('init', help='Run this command in every git repo you want to use jitab')
    parser_init.set_defaults(func=initialize_project)

    parser_new = subparsers.add_parser('new', help='Run this command to pick a new jira issue to work on (read from your input columns)')
    parser_new.set_defaults(func=new_ticket)

    parser_wip = subparsers.add_parser('wip', help='Run this command to continue to work on a jira ticket, but on a different folder (read from your wip columns). This is useful when your task covers multiple tasks')
    parser_wip.set_defaults(func=wip_ticket)

    parser_commit = subparsers.add_parser('commit', help='Run this command to commit your actual work. Commits will be automatically prefixed with jira key (e.g. SQUAD-12)')
    parser_commit.set_defaults(func=commit)
    parser_commit.add_argument ("-m", "--message", type = str, required = True, help = "Specify a commit message")

    parser_mr = subparsers.add_parser('mr', help='Run this command to create a new merge request. Your branch will be pushed and MR associated to it')
    parser_mr.set_defaults(func=mr)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    args.func(args)

def config(args):
    config_file = os.path.expanduser('~/.jitab')
    with open(config_file, 'r') as config:
        config_data = json.load(config)
    jira_username = config_data["jira"]["username"]
    jira_token = config_data["jira"]["token"]
    
    jira_api = JiraAPI(jira_username, jira_token)
    config_service = ConfigService(jira_api)

    project_configuration: Configuration = config_service.run_config()

    if project_configuration:

        config_data["board"] = {}
        config_data["board"]["id"] = project_configuration.board.id
        config_data["board"]["name"] = project_configuration.board.name
        config_data["board"]["projectKey"] = project_configuration.board.projectKey
        config_data["board"]["projectName"] = project_configuration.board.projectName
        config_data["board"]["flow_type"] = project_configuration.board.flow_type
        config_data["board"]["all_columns"] = project_configuration.columns.all_columns
        config_data["board"]["new_columns"] = project_configuration.columns.new_columns
        config_data["board"]["wip_columns"] = project_configuration.columns.wip_columns

        with open(config_file, 'w') as config:
            json.dump(config_data, config, indent = 4)
        
        print(f"You're now tracking board {project_configuration.board.name} with new colunmns {project_configuration.columns.new_columns} and wip columns {project_configuration.columns.wip_columns}")
    else:
        print(f"Configuration not completed. Here's what you got: {project_configuration}")

def initialize_project(args):
    global_config_file = os.path.expanduser('~/.jitab')
    project_config_file = ".jitab"
    project_config_data = {}

    with open(global_config_file, 'r') as config:
        config_data = json.load(config)
    gitlab_username = config_data["gitlab"]["username"]
    gitlab_token = config_data["gitlab"]["token"]

    current_folder_name = os.path.basename(os.getcwd())
    gitlab_api = GitlabAPI(gitlab_username, gitlab_token)
    repo_service = RepoInitService(gitlab_api)

    repository: Repository = repo_service.run_init(current_folder_name)

    if repository:
        project_config_data["id"] = repository.id
        project_config_data["name"] = repository.name
        project_config_data["description"] = repository.description
        project_config_data["path"] = repository.path
        with open(project_config_file, 'w') as config:
            json.dump(project_config_data, config, indent = 4)
        with open(".gitignore", 'a+') as gitignore:
            gitignore.seek(0)
            content = gitignore.read()
            if ".jitab" in content:
                pass
            else:
                gitignore.write("\n.jitab")
        print("Project initialization completed!")
    else:
        print(f"Initialization not completed. Here's what you got: {repository}")


def new_ticket(args):
    read_ticket("new")

def wip_ticket(args):
    read_ticket("wip")

def commit(args):
    git_api = GitAPI()
    commit_result = git_api.commit_changes(args.message)

    if commit_result.returncode != 0:
        print(f"There was an issue while committing your message:")
        print(f"{commit_result.stderr}")
        print(f"{commit_result.stdout}")

def mr(args):
    config_file = os.path.expanduser('~/.jitab')
    project_config_file = ".jitab"
    
    with open(config_file, 'r') as config:
        config_data = json.load(config)
    gitlab_username = config_data["gitlab"]["username"]
    gitlab_token = config_data["gitlab"]["token"]

    with open(project_config_file, 'r') as config:
        project_config_data = json.load(config)
    project_id = project_config_data["id"]

    git_api = GitAPI()
    gitlab_api = GitlabAPI(gitlab_username, gitlab_token)

    current_branch: str = git_api.get_current_branch()
    # Gitlab returns a message making this call ending with status != 0 (message ends up in stderr)
    # We can't check the returncode...
    push_result = git_api.push_changes(current_branch)

    # ... So for now we print out the stdout message
    print(push_result.stdout.decode('utf-8'))

    title = git_api.get_pretty_current_branch()

    mr_result = gitlab_api.create_merge_request(project_id, current_branch, "master", title)
    if mr_result.message == "Created":
        print(f"MR successfully created: {mr_result.link}")

def read_ticket(ticketType: TicketType):
    global_config_file = os.path.expanduser('~/.jitab')

    with open(global_config_file, 'r') as config:
        config_data = json.load(config)

    jira_username = config_data["jira"]["username"]
    jira_token = config_data["jira"]["token"]

    jira_api = JiraAPI(jira_username, jira_token)
    git_api = GitAPI()
    jira_service = JiraService(jira_api)

    flowType: str = config_data["board"]["flow_type"]
    # APIs support reading issues from multiple boards
    # At the moment, nobody works with multiple boards, so just passing a list with one element
    projectKeys: List[str] = [config_data["board"]["projectKey"]]
    statuses: List[str] = []
    if ticketType == "new":
        statuses = config_data["board"]["new_columns"]
    else:
        statuses = config_data["board"]["wip_columns"]

    selected_issue = jira_service.init_work(flowType, projectKeys, statuses)

    if selected_issue:

        branch_result = git_api.create_branch("feature", selected_issue.key, selected_issue.summary)

        if branch_result.returncode != 0:
            print(f"There was an issue while creating git branch: {branch_result.stderr}")