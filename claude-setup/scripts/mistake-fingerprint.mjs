import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'

// Fingerprints for repeated agent mistakes. A fingerprint is a normalized signature: tool, command shape, error class.
// Counts live in a JSON map; an alert fires when one fingerprint recurs enough inside a window, and at most once per window.

export const THRESHOLD = 3
export const WINDOW_DAYS = 14
const DAY_MS = 86_400_000

// Only tools whose first argument is a subcommand. Elsewhere the first word is an argument, not a shape.
const SUBCOMMAND_TOOLS = new Set(['git', 'gh', 'npm', 'pnpm', 'yarn', 'bun', 'uv', 'pip', 'docker', 'kubectl', 'cargo', 'go', 'pueue', 'claude', 'tmux'])

// Subcommands that are groups of their own, so the word after them is also a subcommand.
const SUB_GROUPS = new Set(['pr', 'issue', 'release', 'worktree', 'stash', 'remote', 'compose', 'config'])

// Short fixed list, first match wins. Anything else is 'other', so one unmatched error never splits a count.
const ERROR_CLASSES = [
  ['timeout', /timed? ?out|timeout/i],
  ['permission', /permission denied|EACCES|operation not permitted/i],
  ['not-found', /no such file|not found|ENOENT/i],
  ['unknown-flag', /unknown (option|flag)|unrecognized (option|argument)|invalid option|unexpected argument/i],
  ['denied', /denied|refused|refusing/i],
]

export const errorClass = (text = '') => ERROR_CLASSES.find(([, pattern]) => pattern.test(text))?.[0] ?? 'other'

// "git -C /repo push --force origin main" -> "git push --force". Paths, ids and values are dropped; flag names kept.
// Flags whose next word is a path or value, not part of the shape: "git -C /repo status" is "git status".
const VALUE_FLAGS = new Set(['-C', '-c', '--git-dir', '--work-tree', '--cwd'])

export const commandShape = (command = '') => {
  const [first = '', ...rest] = command.trim().split(/\s+/)
  const program = first.split('/').pop() ?? ''
  const words = rest.filter((token, index) => !VALUE_FLAGS.has(token) && !VALUE_FLAGS.has(rest[index - 1]))
  const flags = [...new Set(words.filter(token => /^--?[A-Za-z]/.test(token)).map(token => token.replace(/=.*/, '')))].sort()
  // A second subcommand word only after a group word: "gh pr create" keeps create; "git push origin" drops origin.
  const candidates = words.filter(token => !token.startsWith('-') && !/[./~$'"]/.test(token))
  const subs = SUBCOMMAND_TOOLS.has(program)
    ? candidates.slice(0, SUB_GROUPS.has(candidates[0]) ? 2 : 1)
    : []
  return [program, ...subs, ...flags].join(' ')
}

export const fingerprint = ({ tool, command, error }) => [tool.toLowerCase(), commandShape(command), errorClass(error)].join('|')

const cutoff = now => now - WINDOW_DAYS * DAY_MS

// Records one occurrence at `now` and drops hits that fell out of the window.
export const recordOccurrence = (map, fp, now) => {
  const entry = map[fp] ?? { hits: [] }
  const hits = [...entry.hits.filter(time => time >= cutoff(now)), now]
  return { ...map, [fp]: { ...entry, hits } }
}

// True once the fingerprint has THRESHOLD hits in the window and has not alerted in the window already.
export const shouldAlert = (entry, now) => {
  if (!entry) return false
  const recent = entry.hits.filter(time => time >= cutoff(now)).length
  const alertedInWindow = entry.alertedAt !== undefined && entry.alertedAt >= cutoff(now)
  return recent >= THRESHOLD && !alertedInWindow
}

export const markAlerted = (map, fp, now) => ({ ...map, [fp]: { ...map[fp], alertedAt: now } })

// CLI: node mistake-fingerprint.mjs --tool Bash --command "..." --error "..." [--map path] [--now ms]
// Silent unless the threshold is reached, so a hook can call it on every failure.
const argValue = name => { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : undefined }

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const mapPath = argValue('map') ?? 'mistakes/fingerprints.json'
  const now = Number(argValue('now') ?? Date.now())
  const fp = fingerprint({ tool: argValue('tool') ?? 'Bash', command: argValue('command'), error: argValue('error') })
  let map = existsSync(mapPath) ? JSON.parse(readFileSync(mapPath, 'utf8')) : {}
  map = recordOccurrence(map, fp, now)
  if (shouldAlert(map[fp], now)) {
    console.log(`ALERT ${fp}: ${map[fp].hits.length} hits in ${WINDOW_DAYS} days. Record a mistake entry for it.`)
    map = markAlerted(map, fp, now)
  }
  writeFileSync(mapPath, `${JSON.stringify(map, null, 2)}\n`)
}
