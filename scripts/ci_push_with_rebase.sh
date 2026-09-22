#!/usr/bin/env bash
set -euo pipefail

branch=${1:?usage: ci_push_with_rebase.sh <branch> [max_attempts]}
max_attempts=${2:-4}
retry_sleep=${PUSH_RETRY_SLEEP:-5}

# Two workflows (and the local dashboard's market-motion publisher) can push to
# the same branch while a long scan is running. Early attempts rebase cleanly or
# fail loudly; from the third attempt on, a content conflict in generated data is
# resolved in favour of THIS run's commit, because losing the day's committed
# scan is worse than one workflow's cache metadata being overwritten.
for ((attempt = 1; attempt <= max_attempts; attempt++)); do
    strategy=()
    if ((attempt >= 3)); then
        echo "::notice title=push-retry::attempt $attempt: resolving data conflicts in favour of this run's commit"
        strategy=(-X theirs)
    fi
    if git pull --rebase --no-autostash ${strategy[@]+"${strategy[@]}"} origin "$branch"; then
        if git push origin "HEAD:$branch"; then
            exit 0
        fi
    else
        git rebase --abort || true
    fi

    if ((attempt < max_attempts)); then
        sleep "$retry_sleep"
    fi
done

echo "::error title=push-failed::could not push to $branch after $max_attempts attempts"
exit 1
