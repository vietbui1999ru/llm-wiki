import { test } from 'node:test'
import assert from 'node:assert/strict'

import { commandShape, errorClass, fingerprint, markAlerted, recordOccurrence, shouldAlert, THRESHOLD, WINDOW_DAYS } from './mistake-fingerprint.mjs'

const DAY = 86_400_000
const NOW = Date.UTC(2026, 9, 15)

test('paths, ids and values do not split one mistake into many', () => {
  assert.equal(commandShape('pytest tests/a.py'), commandShape('pytest tests/b.py'))
  assert.equal(commandShape('docling --output out/x.md in.pdf'), 'docling --output')
})

test('git subcommand is kept even behind -C with a path', () => {
  assert.equal(commandShape('git -C /repo/wt status'), 'git status')
  assert.equal(commandShape('git push --force origin main'), 'git push --force')
})

test('a tool outside the subcommand list does not take its first argument as a shape', () => {
  assert.equal(commandShape('rg foo src'), 'rg')
  assert.equal(commandShape('rg -n foo src'), 'rg -n')
})

test('flag values are dropped, flag names are kept and sorted', () => {
  assert.equal(commandShape('gh pr create --title "x" --draft'), 'gh pr create --draft --title')
})

test('error classes map common messages and fall back to other', () => {
  assert.equal(errorClass('bash: docling: command not found'), 'not-found')
  assert.equal(errorClass('error: unknown option --output-dir'), 'unknown-flag')
  assert.equal(errorClass('Permission denied (publickey)'), 'permission')
  assert.equal(errorClass('something unusual happened'), 'other')
})

test('the same tool and error on different files is one fingerprint; different tools are not', () => {
  const a = fingerprint({ tool: 'Edit', error: 'String to replace not found in file' })
  const b = fingerprint({ tool: 'edit', error: 'String to replace not found in file' })
  const bash = fingerprint({ tool: 'Bash', error: 'String to replace not found in file' })
  assert.equal(a, b)
  assert.notEqual(a, bash)
})

test('alerts only at the threshold, not before', () => {
  let map = {}
  for (let i = 0; i < THRESHOLD - 1; i++) map = recordOccurrence(map, 'fp', NOW + i)
  assert.equal(shouldAlert(map.fp, NOW + THRESHOLD), false)
  map = recordOccurrence(map, 'fp', NOW + THRESHOLD)
  assert.equal(shouldAlert(map.fp, NOW + THRESHOLD), true)
})

test('hits older than the window stop counting', () => {
  let map = {}
  for (let i = 0; i < THRESHOLD; i++) map = recordOccurrence(map, 'fp', NOW - (WINDOW_DAYS + 1) * DAY + i)
  map = recordOccurrence(map, 'fp', NOW)
  assert.equal(shouldAlert(map.fp, NOW), false)
})

test('one alert per window: after alerting, the same fingerprint stays quiet until the window passes', () => {
  let map = {}
  for (let i = 0; i < THRESHOLD; i++) map = recordOccurrence(map, 'fp', NOW + i)
  map = markAlerted(map, 'fp', NOW + THRESHOLD)
  map = recordOccurrence(map, 'fp', NOW + THRESHOLD + 1)
  assert.equal(shouldAlert(map.fp, NOW + THRESHOLD + 1), false)
  assert.equal(shouldAlert(map.fp, NOW + (WINDOW_DAYS + 1) * DAY), false)
})
