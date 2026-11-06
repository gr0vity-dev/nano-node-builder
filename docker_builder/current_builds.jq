# Keep historical records, but only schedule the current head of each open PR.
# PR numbers in older records can be strings or numbers.
def current_builds($pull_requests):
  ($pull_requests | map({key: (.number | tostring), value: .}) | from_entries) as $heads
  | map(select(
      .type != "pull_request" or
      ($heads[(.pull_request | tostring)].head.sha == .hash)
    ))
  # Landed commits always come first, newest first; then current PR heads.
  | sort_by(
      if .type == "commit" then
        [0, -(.landed_at // .created_at | fromdateiso8601)]
      else
        [1, -($heads[(.pull_request | tostring)].updated_at | fromdateiso8601)]
      end
    );
