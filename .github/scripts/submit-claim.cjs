const { readClaim, checkQuota } = require('./claims.cjs');

async function optional(request) {
  try {
    return (await request).data;
  } catch (error) {
    if (error.status !== 404) throw error;
    return null;
  }
}

module.exports = async ({ github, context, now = new Date() }) => {
  const { issue, action, repository } = context.payload;
  if (action !== 'opened' || !issue || issue.pull_request) {
    throw new Error('Only a newly opened issue can register a claim.');
  }
  const hash = (issue.body ?? '').trim().replace(/^### SHA-256\s+/, '').toLowerCase();
  if (!/^[a-f0-9]{64}$/.test(hash)) {
    throw new Error('Paste exactly one SHA-256 hash (64 hexadecimal characters).');
  }

  const repo = context.repo;
  const branch = `claim/${issue.number}`;
  const path = `claims/${issue.number}.txt`;
  const content = `${hash}\n`;
  const { data: prs } = await github.rest.pulls.list({
    ...repo, head: `${repo.owner}:${branch}`, state: 'all', per_page: 100,
  });
  const existing = prs.find(pr => pr.head.repo?.full_name === `${repo.owner}/${repo.repo}`);
  if (existing) {
    const claim = readClaim(existing, repo);
    if (!claim || claim.hash !== hash || claim.user !== String(issue.user.id)) {
      throw new Error('This issue already has a different hash or author. Open a new issue.');
    }
    return existing;
  }
  await checkQuota(github, repo, issue.user.id, now);

  const ref = await optional(github.rest.git.getRef({ ...repo, ref: `heads/${branch}` }));
  if (!ref) {
    const base = await github.rest.git.getRef({
      ...repo, ref: `heads/${repository.default_branch}`,
    });
    await github.rest.git.createRef({
      ...repo, ref: `refs/heads/${branch}`, sha: base.data.object.sha,
    });
  }

  const file = await optional(github.rest.repos.getContent({ ...repo, path, ref: branch }));
  if (file) {
    if (Buffer.from(file.content ?? '', 'base64').toString() !== content) {
      throw new Error('This issue already has a different hash. Open a new issue.');
    }
  } else {
    await github.rest.repos.createOrUpdateFileContents({
      ...repo, path, branch,
      message: `feat: register claim from issue #${issue.number}`,
      content: Buffer.from(content).toString('base64'),
    });
  }

  const { data: pr } = await github.rest.pulls.create({
    ...repo,
    head: branch,
    base: repository.default_branch,
    title: `Claim #${issue.number} by ${issue.user.login}`,
    body: [
      '🤖 AI text below 🤖',
      '',
      `SHA-256: \`${hash}\``,
      '',
      `Submitted by @${issue.user.login}. Use this PR's creation time, recorded by GitHub, as the claim date. Merging is not required for the timestamp.`,
      '',
      'This records a hash, not a review of the work or its authorship.',
      '',
      `Closes #${issue.number}`,
      '',
      `<!-- claim issue=${issue.number} user=${issue.user.id} hash=${hash} -->`,
    ].join('\n'),
  });
  return pr;
};
