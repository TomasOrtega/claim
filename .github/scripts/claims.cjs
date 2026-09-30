const { setTimeout: sleep } = require('node:timers/promises');

function readClaim(pr, repo) {
  if (pr.user?.login !== 'github-actions[bot]' || pr.user.type !== 'Bot'
      || pr.head?.repo?.full_name !== `${repo.owner}/${repo.repo}`) return null;
  const match = /^<!-- claim issue=([1-9]\d*) user=([1-9]\d*) hash=([a-f0-9]{64}) -->$/m.exec(pr.body ?? '');
  if (!match || pr.head.ref !== `claim/${match[1]}`) return null;
  return { issue: match[1], user: match[2], hash: match[3] };
}

async function checkQuota(github, repo, user, now) {
  const day = now.toISOString().slice(0, 10);
  const hour = now.toISOString().slice(0, 13);
  let daily = 0;
  let hourly = 0;
  for await (const { data } of github.paginate.iterator(github.rest.pulls.list, {
    ...repo, state: 'all', sort: 'created', direction: 'desc', per_page: 100,
  })) {
    for (const pr of data) {
      if (pr.created_at.slice(0, 10) < day) return;
      const claim = readClaim(pr, repo);
      if (!claim) continue;
      if (claim.user === String(user)) daily++;
      if (pr.created_at.startsWith(hour)) hourly++;
      let message;
      if (daily >= 1) {
        message = 'The limit is 1 claim per GitHub account per UTC day. No new PR was created. Please submit again after 00:00 UTC.';
      } else if (hourly >= 30) {
        message = 'The repository limit is 30 new claims per UTC hour. No new PR was created. Please submit again next hour.';
      }
      if (message) throw Object.assign(new Error(message), { name: 'ClaimLimitError' });
    }
  }
}

function configureBackoff(github, wait = sleep, now = Date.now) {
  github.hook.wrap('request', async (request, options) => {
    for (let attempt = 0; ; attempt++) {
      try {
        return await request(options);
      } catch (error) {
        const headers = error.response?.headers ?? {};
        const limited = error.status === 429 || (error.status === 403
          && (headers['retry-after'] || headers['x-ratelimit-remaining'] === '0'
            || /rate limit/i.test(error.message)));
        if (!limited || attempt >= 2) throw error;
        let delay = Math.max(60_000 * (attempt + 1), Number(headers['retry-after'] ?? 0) * 1000);
        if (headers['x-ratelimit-remaining'] === '0') {
          delay = Math.max(delay, Number(headers['x-ratelimit-reset']) * 1000 - now() + 1000);
        }
        if (!Number.isFinite(delay) || delay > 120_000) throw error;
        await wait(delay);
      }
    }
  });
}

module.exports = { readClaim, checkQuota, configureBackoff };
