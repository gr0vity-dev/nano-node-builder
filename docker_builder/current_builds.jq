# Keep historical records, but only schedule the current head of each open PR.
# PR numbers in older records can be strings or numbers.
def current_builds($pull_requests):
  ($pull_requests | map({key: (.number | tostring), value: .}) | from_entries) as $heads
  | map(select(
      .type != "pull_request" or
      ($heads[(.pull_request | tostring)].head.sha == .hash)
    ))
  # One queue for both types: newest landing or PR update first.
  | sort_by(
      -(if .type == "commit" then
          .landed_at // .created_at
        else
          $heads[(.pull_request | tostring)].updated_at
        end | fromdateiso8601),
      .hash
    );
