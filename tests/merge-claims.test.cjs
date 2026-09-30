const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const test = require('node:test');
const merge = require('../.github/scripts/merge-claims.cjs');

const HASH = 'ab'.repeat(32);

function fixture() {
  const pr = {
    number: 13,
    state: 'open',
    draft: false,
    user: { login: 'github-actions[bot]', type: 'Bot' },
    head: { ref: 'claim/12', sha: 'claim-commit', repo: { full_name: 'example/claim' } },
    base: { ref: 'main', sha: 'base-commit' },
    body: `<!-- claim issue=12 user=123 hash=${HASH} -->`,
  };
  const state = {
    prs: [pr],
    files: [{ filename: 'claims/12.txt', status: 'added' }],
    file: { type: 'file', content: Buffer.from(`${HASH}\n`).toString('base64') },
    merged: [], deleted: [], sleeps: [], warnings: [], branchSha: 'claim-commit',
  };
  const github = {
    rest: {
      pulls: {
        list: Symbol('pulls'),
        async get({ pull_number }) {
          return { data: state.prs.find(item => item.number === pull_number) };
        },
        async merge(params) {
          if (state.mergeError) throw Object.assign(new Error('Cannot merge'), { status: state.mergeError });
          assert.equal(params.sha, 'claim-commit');
          assert.equal(params.merge_method, 'squash');
          state.merged.push(params.pull_number);
          state.prs.find(item => item.number === params.pull_number).state = 'closed';
          return { data: { merged: true } };
        },
      },
      repos: {
        async compareCommitsWithBasehead(params) {
          assert.equal(params.basehead, 'base-commit...claim-commit');
          return { data: { files: state.files } };
        },
        async getContent(params) {
          assert.equal(params.path, 'claims/12.txt');
          assert.equal(params.ref, 'claim-commit');
          return { data: state.file };
        },
      },
      git: {
        async getRef() {
          if (state.branchSha === null) throw Object.assign(new Error('Not found'), { status: 404 });
          return { data: { object: { sha: state.branchSha } } };
        },
        async deleteRef({ ref }) { state.deleted.push(ref); },
      },
    },
    async paginate(method, params) {
      assert.equal(method, github.rest.pulls.list);
      assert.equal(params.state, 'open');
      assert.equal(params.base, 'main');
      return state.prs.filter(item => item.state === 'open');
    },
  };
  const run = (options = {}) => merge({
    github,
    context: { repo: { owner: 'example', repo: 'claim' }, payload: { repository: { default_branch: 'main' } } },
    core: { warning: message => state.warnings.push(message) },
    sleep: async ms => state.sleeps.push(ms),
    ...options,
  });
  return { state, pr, run };
}

test('merges only the validated commit and deletes its branch', async () => {
  const { state, run } = fixture();
  await run();
  assert.deepEqual(state.merged, [13]);
  assert.deepEqual(state.deleted, ['heads/claim/12']);
});

test('skips human PRs, forks, drafts, other bases, and invalid metadata', async () => {
  for (const change of [
    { user: { login: 'Alice', type: 'User' } },
    { head: { ref: 'claim/12', repo: { full_name: 'outsider/claim' } } },
    { head: { ref: 'other-branch', repo: { full_name: 'example/claim' } } },
    { draft: true },
    { base: { ref: 'other' } },
    { body: '<!-- claim issue=12 user=123 hash=invalid -->' },
  ]) {
    const { state, pr, run } = fixture();
    Object.assign(pr, change);
    await run();
    assert.deepEqual(state.merged, []);
    assert.deepEqual(state.deleted, []);
  }
});

test('rejects extra files, wrong paths, modifications, and mismatched hashes', async () => {
  for (const files of [
    [{ filename: 'claims/12.txt', status: 'added' }, { filename: '.github/workflows/ci.yml', status: 'modified' }],
    [{ filename: 'claims/99.txt', status: 'added' }],
    [{ filename: 'claims/12.txt', status: 'modified' }],
    [],
  ]) {
    const { state, run } = fixture();
    state.files = files;
    await run();
    assert.deepEqual(state.merged, []);
  }
  for (const file of [
    { type: 'symlink', content: Buffer.from(`${HASH}\n`).toString('base64') },
    { type: 'file', content: Buffer.from('cd'.repeat(32) + '\n').toString('base64') },
  ]) {
    const { state, run } = fixture();
    state.file = file;
    await run();
    assert.deepEqual(state.merged, []);
  }
});

test('head changes and merge protection failures never trigger branch deletion', async () => {
  for (const status of [409, 405]) {
    const { state, run } = fixture();
    state.mergeError = status;
    await run();
    assert.deepEqual(state.deleted, []);
  }
});

test('preserves a branch that has changed after merging and tolerates automatic deletion', async () => {
  for (const sha of ['new-commit', null]) {
    const { state, run } = fixture();
    state.branchSha = sha;
    await run();
    assert.deepEqual(state.merged, [13]);
    assert.deepEqual(state.deleted, []);
  }
});

test('paces merge attempts one minute apart and caps each run', async () => {
  const { state, pr, run } = fixture();
  state.prs.push({ ...pr, number: 14 }, { ...pr, number: 15 });
  await run({ maxMerges: 2 });
  assert.deepEqual(state.merged, [13, 14]);
  assert.deepEqual(state.sleeps, [60_000, 60_000]);
});

test('the daily workflow can clear a full day of accepted claims across its batches', async () => {
  const workflow = readFileSync(join(__dirname, '../.github/workflows/merge-claims.yml'), 'utf8');
  const matrix = workflow.match(/^\s+batch: (\[[\d,\s]+\])$/m);
  const batches = matrix ? JSON.parse(matrix[1]) : [1];
  const { state, pr, run } = fixture();
  state.prs = Array.from({ length: 30 * 24 }, (_, i) => ({ ...pr, number: i + 13 }));
  for (let batch = 0; batch < batches.length; batch++) {
    await run();
  }
  assert.equal(state.merged.length, 30 * 24);
  assert.equal(new Set(state.merged).size, 30 * 24);
  assert.equal(state.sleeps.length, 30 * 24);
});

test('stops on API failures instead of continuing to hammer GitHub', async () => {
  const { state, run } = fixture();
  state.mergeError = 429;
  await assert.rejects(run, /Cannot merge/);
  assert.deepEqual(state.deleted, []);
});
