const assert = require('node:assert/strict');
const test = require('node:test');
const { configureBackoff } = require('../.github/scripts/claims.cjs');

function fixture(error) {
  let wrapped;
  const waits = [];
  let calls = 0;
  configureBackoff({ hook: { wrap(name, callback) {
    assert.equal(name, 'request');
    wrapped = callback;
  } } }, async delay => waits.push(delay), () => 0);
  return {
    waits,
    calls: () => calls,
    run: (failures = 1) => wrapped(async () => {
      if (++calls <= failures) throw error;
      return 'ok';
    }, {}),
  };
}

test('respects Retry-After on secondary rate limits', async () => {
  const { run, waits } = fixture({ status: 429, response: { headers: { 'retry-after': '90' } } });
  assert.equal(await run(), 'ok');
  assert.deepEqual(waits, [90_000]);
});

test('waits beyond the primary rate-limit reset when it fits the retry budget', async () => {
  const { run, waits } = fixture({ status: 403, response: {
    headers: { 'x-ratelimit-remaining': '0', 'x-ratelimit-reset': '90' },
  } });
  assert.equal(await run(), 'ok');
  assert.deepEqual(waits, [91_000]);
});

test('bounds retries for repeated throttling', async () => {
  const { run, waits, calls } = fixture({ status: 403, message: 'API rate limit exceeded' });
  await assert.rejects(run(10));
  assert.deepEqual(waits, [60_000, 120_000]);
  assert.equal(calls(), 3);
});

test('does not retry permission errors or ignore long server-requested waits', async () => {
  for (const error of [
    { status: 403, message: 'Resource not accessible by integration' },
    { status: 404 },
    { status: 429, response: { headers: { 'retry-after': '180' } } },
    { status: 403, response: { headers: { 'x-ratelimit-remaining': '0', 'x-ratelimit-reset': '3600' } } },
  ]) {
    const { run, waits, calls } = fixture(error);
    await assert.rejects(run());
    assert.deepEqual(waits, []);
    assert.equal(calls(), 1);
  }
});
