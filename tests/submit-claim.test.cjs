const assert = require('node:assert/strict');
const test = require('node:test');
const submit = require('../.github/scripts/submit-claim.cjs');

const HASH = 'ab'.repeat(32);
const missing = () => Object.assign(new Error('Not found'), { status: 404 });

function fixture() {
  const state = { branch: false, file: null, prs: [], fail: false, pages: [] };
  const context = {
    repo: { owner: 'example', repo: 'claim' },
    payload: {
      action: 'opened',
      repository: { default_branch: 'main' },
      sender: { login: 'maintainer' },
      issue: {
        number: 12,
        body: `### SHA-256\n\n${HASH}`,
        user: { login: 'Alice', id: 123 },
        html_url: 'https://github.com/example/claim/issues/12',
      },
    },
  };
  const github = {
    rest: {
      git: {
        async getRef({ ref }) {
          if (ref !== 'heads/main' && !state.branch) throw missing();
          return { data: { object: { sha: 'base-commit' } } };
        },
        async createRef(params) {
          assert.equal(params.ref, 'refs/heads/claim/12');
          assert.equal(params.sha, 'base-commit');
          state.branch = true;
        },
      },
      repos: {
        async getContent(params) {
          assert.equal(params.path, 'claims/12.txt');
          assert.equal(params.ref, 'claim/12');
          if (!state.file) throw missing();
          return { data: { content: state.file.content, encoding: 'base64' } };
        },
        async createOrUpdateFileContents(params) {
          assert.ok(state.branch);
          assert.equal(params.branch, 'claim/12');
          assert.equal(params.path, 'claims/12.txt');
          assert.equal(state.file, null);
          state.file = params;
        },
      },
      pulls: {
        async list(params) {
          assert.equal(params.state, 'all');
          assert.equal(params.head, 'example:claim/12');
          return { data: state.prs };
        },
        async create(params) {
          if (state.fail) {
            state.fail = false;
            throw new Error('Temporary API failure');
          }
          assert.equal(params.head, 'claim/12');
          assert.equal(params.base, 'main');
          const pr = {
            ...params,
            user: { login: 'github-actions[bot]', type: 'Bot' },
            head: { ref: params.head, repo: { full_name: 'example/claim' } },
            html_url: 'https://github.com/example/claim/pull/13',
            created_at: '2026-09-30T12:00:00Z',
          };
          state.prs.push(pr);
          return { data: pr };
        },
      },
    },
    paginate: {
      async *iterator(method, params) {
        assert.equal(method, github.rest.pulls.list);
        assert.equal(params.state, 'all');
        assert.equal(params.sort, 'created');
        assert.equal(params.direction, 'desc');
        assert.equal(params.per_page, 100);
        for (const page of state.pages) yield { data: page };
      },
    },
  };
  return {
    state, context,
    run: () => submit({ github, context, now: new Date('2026-09-30T12:00:00Z') }),
  };
}

test('turns the opening issue hash into a PR attributed to its author', async () => {
  const { state, run } = fixture();
  const pr = await run();
  assert.equal(pr.html_url, 'https://github.com/example/claim/pull/13');
  assert.equal(Buffer.from(state.file.content, 'base64').toString(), `${HASH}\n`);
  assert.ok(pr.body.startsWith('🤖 AI text below 🤖\n'));
  assert.ok(pr.body.includes(`SHA-256: \`${HASH}\``));
  assert.ok(pr.body.includes('@Alice'));
  assert.ok(pr.body.includes("this PR's creation time"));
  assert.ok(pr.body.includes('Closes #12'));
  assert.ok(!pr.body.includes('maintainer'));
});

test('accepts a bare hash and normalizes uppercase and CRLF', async () => {
  const { context, run } = fixture();
  context.payload.issue.body = `${HASH.toUpperCase()}\r\n`;
  assert.ok((await run()).body.includes(HASH));
});

test('reruns reuse the PR and preserve its timestamp, even after closing', async () => {
  const { state, run } = fixture();
  const original = await run();
  original.state = 'closed';
  state.branch = false;
  state.file = null;
  assert.deepEqual(await run(), original);
  assert.equal(state.prs.length, 1);
  assert.equal(state.branch, false);
});

test('retries recover after the file was written but PR creation failed', async () => {
  const { state, run } = fixture();
  state.fail = true;
  await assert.rejects(run, /Temporary API failure/);
  const file = structuredClone(state.file);
  assert.equal((await run()).html_url, 'https://github.com/example/claim/pull/13');
  assert.deepEqual(state.file, file);
  assert.equal(state.prs.length, 1);
});

test('a different hash cannot overwrite an existing claim or inherit its date', async () => {
  const { state, context, run } = fixture();
  await run();
  context.payload.issue.body = 'cd'.repeat(32);
  await assert.rejects(run, /different hash/);
  assert.equal(state.prs.length, 1);
  assert.equal(Buffer.from(state.file.content, 'base64').toString(), `${HASH}\n`);
});

test('rejects edited issues and PR events before writing anything', async () => {
  for (const change of [{ action: 'edited' }, { issue: { pull_request: {} } }]) {
    const { state, context, run } = fixture();
    Object.assign(context.payload, change);
    await assert.rejects(run, /newly opened issue/);
    assert.equal(state.branch, false);
  }
});

test('rejects malformed hashes, filenames, and multiple hashes before writing', async () => {
  for (const body of [null, '', 'a'.repeat(63), 'a'.repeat(65), 'g'.repeat(64),
    `${HASH}  work.zip`, `${HASH}\n${HASH}`, `${HASH}\n${'cd'.repeat(32)}`]) {
    const { state, context, run } = fixture();
    context.payload.issue.body = body;
    await assert.rejects(run, /exactly one SHA-256 hash/);
    assert.equal(state.branch, false);
  }
});

function accepted(issue, user = 123, created = '2026-09-30T11:00:00Z') {
  return {
    user: { login: 'github-actions[bot]', type: 'Bot' },
    head: { ref: `claim/${issue}`, repo: { full_name: 'example/claim' } },
    body: `<!-- claim issue=${issue} user=${user} hash=${HASH} -->`,
    created_at: created,
    state: 'closed',
    merged_at: created,
  };
}

test('rejects the second accepted claim across pages before creating a branch', async () => {
  const { state, run } = fixture();
  state.pages = [[accepted(100, 456)], [accepted(200)]];
  await assert.rejects(run, /1 claim per GitHub account per UTC day/);
  assert.equal(state.branch, false);
  assert.equal(state.file, null);
});

test('allows the first claim and counts account IDs across username changes', async () => {
  const { state, context, run } = fixture();
  const original = await run();
  assert.ok(original.body.includes('@Alice'));
  assert.ok(original.body.includes('user=123'));
  state.prs = [];
  state.pages = [[original]];
  context.payload.issue.user.login = 'RenamedAlice';
  await assert.rejects(run, /1 claim per GitHub account per UTC day/);
});

test('ignores prior UTC days, other accounts, and forged claim metadata', async () => {
  const { state, run } = fixture();
  state.pages = [[
    accepted(100, 456),
    { ...accepted(200), user: { login: 'Alice', type: 'User' } },
    accepted(300, 123, '2026-09-29T23:59:59Z'),
  ]];
  await run();
  assert.equal(state.prs.length, 1);
});

test('rejects new claims after 30 accepted claims in the current UTC hour', async () => {
  const { state, run } = fixture();
  state.pages = [Array.from({ length: 30 }, (_, i) => accepted(i + 100, i + 1000, '2026-09-30T12:00:00Z'))];
  await assert.rejects(run, /30 new claims per UTC hour/);
  assert.equal(state.branch, false);
});

test('earlier UTC hours do not consume the repository hourly quota', async () => {
  const { state, run } = fixture();
  state.pages = [Array.from({ length: 30 }, (_, i) => accepted(i + 100, i + 1000))];
  await run();
  assert.equal(state.prs.length, 1);
});

test('an existing claim can be retried even when the account quota is full', async () => {
  const { state, run } = fixture();
  const original = await run();
  state.pages = [[original]];
  assert.deepEqual(await run(), original);
  assert.equal(state.prs.length, 1);
});
