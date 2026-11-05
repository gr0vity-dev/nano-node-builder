# Keep historical records, but only schedule the current head of each open PR.
# PR numbers in older records can be strings or numbers.
def current_builds($pull_requests):
  ($pull_requests | map({key: (.number | tostring), value: .}) | from_entries) as $heads
  | map(select(
      .type != "pull_request" or
      ($heads[(.pull_request | tostring)].head.sha == .hash)
    ))
  # Give recently updated PRs priority over the develop-commit backlog.
  | sort_by(
      if .type == "pull_request" then
        [0, -($heads[(.pull_request | tostring)].updated_at | fromdateiso8601)]
      else
        [1, .created_at]
      end
    );
