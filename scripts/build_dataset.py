"""Build data/servers/*.json from the raw tool lists and our labels.

Labels follow the rubric in README.md: P private data, U untrusted content,
E external communication (free text written where others can read it, or a
request to an outside address). Every label carries its reason.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

R = {
    "repo_read": "returns content from repositories the token can read: private ones (P) and ones others write to (U)",
    "gh_private_meta": "returns account or organisation details outsiders cannot see",
    "gh_search": "searches all of GitHub, including private repositories the token can read: results are written by others",
    "gh_search_public": "searches public profiles written by their owners",
    "gh_write_text": "writes free text (body, title, content or message) into a repository, issue or pull request that others can read",
    "gh_no_text": "changes state without a free-text field others can read",
    "gh_pending": "pending review comments are visible only to their author until the review is submitted",
    "gh_copilot": "its custom_instructions reach Copilot, not other people",
    "sb_private": "returns account, project or database details outsiders cannot see",
    "sb_sql": "runs any SQL: reads private tables (P) whose rows app users write (U), and can write rows the app shows to its users (E), the setup of the July 2025 Supabase demonstration",
    "sb_migration": "applies SQL that can also insert or change rows the app shows to its users",
    "sb_logs": "returns request logs: private, and partly written by whoever calls the project",
    "sb_deploy": "deploys code that runs publicly and can send data anywhere",
    "sb_none": "changes or reads project state with no private payload and no free text others read",
    "sb_docs": "first-party Supabase documentation, not text an attacker can write",
    "sb_keys": "publishable keys are designed to be public",
    "pw_read": "returns content of pages the browser has open: written by the site (U), and private when the persistent profile is logged in (P)",
    "pw_navigate": "loads any URL (E: data can ride in the URL) and returns the page (P, U)",
    "pw_input": "types, clicks or submits into a web page, which can send text to that site",
    "pw_code": "runs arbitrary JavaScript, which can read the page and call any address",
    "pw_upload": "uploads local files to a website",
    "pw_none": "changes browser state without reading page content or sending data",
    "nt_read": "returns workspace pages, blocks, comments or users: private to the workspace (P), partly written by teammates and guests (U)",
    "nt_users": "returns workspace member details outsiders cannot see",
    "nt_write": "writes free text into a page, block, comment or data source that teammates, guests or public-page visitors can read",
    "nt_none": "moves or deletes without writing text others read",
    "sl_read": "returns channel, DM or thread messages: private to the workspace (P), written by other people (U)",
    "sl_private": "returns workspace directory details outsiders cannot see",
    "sl_groups": "returns user groups and their descriptions, written by other members",
    "sl_group_text": "writes a group name, handle or description that every member of the workspace can read",
    "sl_none": "changes the user's own state without text others read",
    "fs_read": "returns local files",
    "fs_none": "changes local files only, and nothing leaves the machine",
    "mem_read": "returns the stored memory graph",
    "mem_none": "changes local memory only",
    "fetch": "fetches any URL: the page is written by its owner (U), and data can leave in the URL (E)",
    "git_read": "returns repository history and diffs: private code (P), with commits often written by other people (U)",
    "git_status": "returns local working tree state",
    "git_none": "changes the local repository only, and there is no push tool",
}

LABELS = {
    "github": {
        **{n: ("PU", "repo_read") for n in ["get_commit", "get_file_contents", "get_label", "get_latest_release", "get_release_by_tag", "get_tag", "issue_read", "list_branches", "list_commits", "list_issue_fields", "list_issue_types", "list_issues", "list_pull_requests", "list_releases", "list_tags", "pull_request_read", "ui_get"]},
        **{n: ("P", "gh_private_meta") for n in ["get_me", "get_team_members", "get_teams", "list_repository_collaborators"]},
        **{n: ("PU", "gh_search") for n in ["search_code", "search_commits", "search_issues", "search_pull_requests", "search_repositories"]},
        "search_users": ("U", "gh_search_public"),
        **{n: ("E", "gh_write_text") for n in ["add_issue_comment", "add_reply_to_pull_request_comment", "create_or_update_file", "create_pull_request", "create_repository", "delete_file", "issue_write", "merge_pull_request", "pull_request_review_write", "push_files", "update_issue_comment", "update_pull_request"]},
        **{n: ("", "gh_no_text") for n in ["create_branch", "fork_repository", "request_copilot_review", "sub_issue_write", "update_pull_request_branch"]},
        "add_comment_to_pending_review": ("", "gh_pending"),
        "assign_copilot_to_issue": ("", "gh_copilot"),
    },
    "supabase": {
        **{n: ("P", "sb_private") for n in ["list_organizations", "get_organization", "list_projects", "get_project", "list_tables", "list_extensions", "list_migrations", "get_advisors", "generate_typescript_types", "list_edge_functions", "get_edge_function", "list_branches", "list_storage_buckets", "get_storage_config"]},
        "execute_sql": ("PUE", "sb_sql"),
        "apply_migration": ("E", "sb_migration"),
        "query_logs": ("PU", "sb_logs"),
        "deploy_edge_function": ("E", "sb_deploy"),
        **{n: ("", "sb_none") for n in ["get_cost", "confirm_cost", "create_project", "pause_project", "restore_project", "create_branch", "delete_branch", "merge_branch", "reset_branch", "rebase_branch", "update_storage_config", "get_project_url"]},
        "search_docs": ("", "sb_docs"),
        "get_publishable_keys": ("", "sb_keys"),
    },
    "playwright": {
        **{n: ("PU", "pw_read") for n in ["browser_console_messages", "browser_find", "browser_network_requests", "browser_network_request", "browser_take_screenshot", "browser_snapshot", "browser_navigate_back"]},
        "browser_navigate": ("PUE", "pw_navigate"),
        **{n: ("E", "pw_input") for n in ["browser_fill_form", "browser_press_key", "browser_type", "browser_click", "browser_select_option", "browser_drag"]},
        **{n: ("PUE", "pw_code") for n in ["browser_evaluate", "browser_run_code_unsafe"]},
        **{n: ("PE", "pw_upload") for n in ["browser_file_upload", "browser_drop"]},
        **{n: ("", "pw_none") for n in ["browser_close", "browser_resize", "browser_handle_dialog", "browser_emulate_media", "browser_hover", "browser_tabs", "browser_wait_for"]},
    },
    "notion": {
        **{n: ("PU", "nt_read") for n in ["API-post-search", "API-get-block-children", "API-retrieve-a-block", "API-retrieve-a-page", "API-retrieve-a-page-property", "API-retrieve-a-comment", "API-query-data-source", "API-retrieve-a-data-source", "API-list-data-source-templates", "API-retrieve-a-database", "API-retrieve-page-markdown"]},
        **{n: ("P", "nt_users") for n in ["API-get-user", "API-get-users", "API-get-self"]},
        **{n: ("E", "nt_write") for n in ["API-patch-block-children", "API-update-a-block", "API-patch-page", "API-post-page", "API-create-a-comment", "API-update-a-data-source", "API-create-a-data-source", "API-update-page-markdown"]},
        **{n: ("", "nt_none") for n in ["API-delete-a-block", "API-move-page"]},
    },
    "slack": {
        **{n: ("PU", "sl_read") for n in ["conversations_history", "conversations_replies", "conversations_search_messages", "conversations_unreads"]},
        **{n: ("P", "sl_private") for n in ["users_search", "channels_list", "channels_me"]},
        "usergroups_list": ("PU", "sl_groups"),
        **{n: ("E", "sl_group_text") for n in ["usergroups_create", "usergroups_update"]},
        **{n: ("", "sl_none") for n in ["conversations_mark", "conversations_leave", "conversations_join", "usergroups_me", "usergroups_users_update", "saved_update", "saved_clear_completed"]},
    },
    "filesystem": {
        **{n: ("P", "fs_read") for n in ["read_file", "read_text_file", "read_media_file", "read_multiple_files", "list_directory", "list_directory_with_sizes", "directory_tree", "search_files", "get_file_info", "list_allowed_directories"]},
        **{n: ("", "fs_none") for n in ["write_file", "edit_file", "create_directory", "move_file"]},
    },
    "memory": {
        **{n: ("P", "mem_read") for n in ["read_graph", "search_nodes", "open_nodes"]},
        **{n: ("", "mem_none") for n in ["create_entities", "create_relations", "add_observations", "delete_entities", "delete_observations", "delete_relations"]},
    },
    "fetch": {"fetch": ("UE", "fetch")},
    "git": {
        **{n: ("PU", "git_read") for n in ["git_diff_unstaged", "git_diff_staged", "git_diff", "git_log", "git_show"]},
        **{n: ("P", "git_status") for n in ["git_status", "git_branch"]},
        **{n: ("", "git_none") for n in ["git_commit", "git_add", "git_reset", "git_create_branch", "git_checkout"]},
    },
}


def build():
    out = ROOT / "data" / "servers"
    out.mkdir(parents=True, exist_ok=True)
    for server, labels in LABELS.items():
        raw = json.loads((ROOT / "data" / "raw" / f"{server}.json").read_text())
        tools = [t for t in raw["tools"] if t.get("_default_on", True)]
        names = {t["name"] for t in tools}
        if names != set(labels):
            raise SystemExit(f"{server}: unlabelled {sorted(names - set(labels))}, unknown {sorted(set(labels) - names)}")
        result = []
        for t in tools:
            letters, reason = labels[t["name"]]
            result.append({
                "name": t["name"],
                "description": " ".join(t.get("description", "").split()),
                "inputSchema": t.get("inputSchema"),
                "annotations": t.get("annotations"),
                "labels": [l for l in "PUE" if l in letters],
                "reasons": {l: R[reason] for l in letters} if letters else {"none": R[reason]},
            })
        doc = {"server": server, "serverInfo": {k: v for k, v in raw.get("serverInfo", {}).items() if k in ("name", "title", "version")},
               "listing": raw.get("_listing", "tools/list over stdio, network off"), "tools": result}
        (out / f"{server}.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        print(server, len(result), "tools,", "".join(sorted({l for t in result for l in t["labels"]}, key="PUE".index)))


if __name__ == "__main__":
    build()
