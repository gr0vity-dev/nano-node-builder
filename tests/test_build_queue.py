import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


def pr(number, head, updated_at="2026-11-05T10:00:00Z"):
    return {"number": number, "head": {"sha": head}, "updated_at": updated_at}


def build(sha, number=None, status=None, created_at="2026-11-01T10:00:00Z"):
    return {
        "hash": sha,
        "type": "pull_request" if number is not None else "commit",
        "pull_request": number,
        "build_status": status,
        "created_at": created_at,
    }


def queue(builds, prs, selection="."):
    result = subprocess.run(
        [
            "jq", "-L", str(ROOT / "docker_builder"),
            "--argjson", "prs", json.dumps(prs),
            'include "current_builds"; current_builds($prs) | ' + selection,
        ],
        input=json.dumps(builds), text=True, capture_output=True, check=True,
    )
    return json.loads(result.stdout)


class BuildQueueTests(unittest.TestCase):
    def test_only_current_head_of_each_pr_is_kept(self):
        builds = [build("old", 1), build("new", 1), build("other", 2)]
        self.assertEqual(
            [b["hash"] for b in queue(builds, [pr(1, "new"), pr(2, "other")])],
            ["new", "other"],
        )

    def test_pr_numbers_can_be_strings(self):
        self.assertEqual(queue([build("head", "123")], [pr(123, "head")])[0]["hash"], "head")

    def test_closed_prs_are_skipped(self):
        self.assertEqual(queue([build("closed", 1)], []), [])

    def test_force_push_uses_live_head_instead_of_record_dates(self):
        builds = [build("old", 1), build("force-pushed", 1, created_at="2025-01-01T00:00:00Z")]
        self.assertEqual(queue(builds, [pr(1, "force-pushed")]), [builds[1]])

    def test_missing_new_head_never_falls_back_to_obsolete_image(self):
        self.assertEqual(queue([build("old", 1, "pass")], [pr(1, "not-built-yet")]), [])

    def test_recent_pr_heads_precede_older_landed_commits(self):
        builds = [build("develop"), build("older-pr", 1), build("newer-pr", 2)]
        prs = [pr(1, "older-pr"), pr(2, "newer-pr", "2026-11-05T11:00:00Z")]
        self.assertEqual([b["hash"] for b in queue(builds, prs)], ["newer-pr", "older-pr", "develop"])

    def test_newest_landed_commit_is_first_and_older_commits_remain_eligible(self):
        builds = [
            build("old-landed", created_at="2026-11-01T10:00:00Z"),
            build("pr-head", 1),
            build("latest-landed", created_at="2026-11-06T10:00:00Z"),
        ]
        self.assertEqual(
            [b["hash"] for b in queue(builds, [pr(1, "pr-head")])],
            ["latest-landed", "pr-head", "old-landed"],
        )

    def test_landing_date_takes_priority_over_original_author_date(self):
        latest = build("just-landed", created_at="2025-01-01T00:00:00Z")
        latest["landed_at"] = "2026-11-06T12:00:00Z"
        older = build("previously-landed", created_at="2026-11-05T10:00:00Z")
        self.assertEqual(queue([older, latest], []), [latest, older])

    def test_both_build_and_test_queues_can_select_pr_before_commit(self):
        prs = [pr(1, "new-pr")]
        pending = [build("old-commit"), build("new-pr", 1)]
        self.assertEqual(
            queue(pending, prs, 'map(select(.build_status == null)) | .[0].hash'),
            "new-pr",
        )
        ready = [dict(b, build_status="pass") for b in pending]
        self.assertEqual(
            queue(ready, prs, 'map(select(.build_status == "pass")) | .[0].hash'),
            "new-pr",
        )

    def test_unbuilt_newest_pr_does_not_block_ready_images(self):
        builds = [build("new-pr", 1), build("ready-commit", status="pass")]
        self.assertEqual(
            queue(builds, [pr(1, "new-pr")],
                  'map(select(.build_status == "pass")) | .[0].hash'),
            "ready-commit",
        )

    def test_built_head_does_not_reactivate_pending_ancestors(self):
        self.assertEqual(
            queue([build("old", 1), build("head", 1, "pass")], [pr(1, "head")],
                  'map(select(.build_status == null)) | .[0].hash'),
            None,
        )

    def test_tests_wait_for_latest_head_to_build(self):
        self.assertEqual(
            queue([build("old", 1, "pass"), build("head", 1)], [pr(1, "head")],
                  'map(select(.build_status == "pass"))'),
            [],
        )

    def test_develop_commits_remain_eligible_without_open_prs(self):
        builds = [build("develop", status="pass")]
        self.assertEqual(queue(builds, []), builds)


if __name__ == "__main__":
    unittest.main()
