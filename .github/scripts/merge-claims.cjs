const { setTimeout: sleep } = require('node:timers/promises');
const { readClaim } = require('./claims.cjs');

module.exports = async ({ github, context, core, sleep: wait = sleep, maxMerges = 300 }) => {
  const repo = context.repo;
  const base = context.payload.repository.default_branch;
  const prs = await github.paginate(github.rest.pulls.list, {
    ...repo, state: 'open', base, sort: 'created', direction: 'asc', per_page: 100,
  });
  let attempts = 0;
  let merged = 0;
  for (const candidate of prs) {
    if (attempts >= maxMerges) break;
    if (!readClaim(candidate, repo) || candidate.draft) continue;
    const { data: pr } = await github.rest.pulls.get({ ...repo, pull_number: candidate.number });
    const claim = readClaim(pr, repo);
    if (!claim || pr.draft || pr.state !== 'open' || pr.base.ref !== base) continue;
    const path = `claims/${claim.issue}.txt`;
    const { data: diff } = await github.rest.repos.compareCommitsWithBasehead({
      ...repo, basehead: `${pr.base.sha}...${pr.head.sha}`,
    });
    if (diff.files?.length !== 1 || diff.files[0].filename !== path || diff.files[0].status !== 'added') {
      core.warning(`Skipping PR #${pr.number}: expected exactly one new claim file.`);
      continue;
    }
    const { data: file } = await github.rest.repos.getContent({ ...repo, path, ref: pr.head.sha });
    if (file.type !== 'file' || Buffer.from(file.content ?? '', 'base64').toString() !== `${claim.hash}\n`) {
      core.warning(`Skipping PR #${pr.number}: file does not match the recorded hash.`);
      continue;
    }
    // Include the first merge to preserve spacing between sequential batches.
    await wait(60_000);
    attempts++;
    try {
      const { data: result } = await github.rest.pulls.merge({
        ...repo, pull_number: pr.number, sha: pr.head.sha, merge_method: 'squash',
        commit_title: `feat: register claim #${claim.issue}`,
      });
      if (!result.merged) {
        core.warning(`PR #${pr.number} was not merged: ${result.message}`);
        continue;
      }
    } catch (error) {
      if (![405, 409].includes(error.status)) throw error;
      core.warning(`Skipping PR #${pr.number}: its head changed or GitHub blocked the merge.`);
      continue;
    }
    merged++;
    try {
      const ref = `heads/${pr.head.ref}`;
      const { data } = await github.rest.git.getRef({ ...repo, ref });
      if (data.object.sha === pr.head.sha) await github.rest.git.deleteRef({ ...repo, ref });
      else core.warning(`Keeping ${pr.head.ref}: it changed after merging.`);
    } catch (error) {
      if (error.status !== 404) throw error;
    }
  }
  return merged;
};
