'use strict';
// Long-lived Node process for tests/node_runner.py: runs each `node -` script in-process instead of paying a
// process start per call. One JSON request per line in, one JSON reply per line out. Each script gets its own
// captured process.stdout/stderr and console; scripts keep their state in their own vm contexts.
const Module = require('node:module');
const path = require('node:path');
const readline = require('node:readline');
const { Console } = require('node:console');
const { Writable } = require('node:stream');

const root = path.resolve(__dirname, '..');
const reply = process.stdout.write.bind(process.stdout);
const filename = path.join(root, '[stdin]');
const requireFromRoot = Module.createRequire(filename);

const baselineGlobals = new Set(Object.getOwnPropertyNames(globalThis));

class ExitSignal { constructor(code) { this.code = code; } }

async function runScript(script) {
  let stdout = '';
  let stderr = '';
  let code = 0;
  const text = chunk => (typeof chunk === 'string' ? chunk : Buffer.from(chunk).toString());
  const sink = append => new Writable({ decodeStrings: false, write(chunk, _encoding, done) { append(text(chunk)); done(); } });
  const outStream = sink(chunk => { stdout += chunk; });
  const errStream = sink(chunk => { stderr += chunk; });
  const fakeProcess = Object.create(process);
  Object.defineProperties(fakeProcess, {
    stdout: { value: outStream },
    stderr: { value: errStream },
    exit: { value: exitCode => { throw new ExitSignal(exitCode ?? code); } },
    exitCode: { get: () => code, set: value => { code = value; } },
  });
  const fakeConsole = new Console({ stdout: outStream, stderr: errStream });
  try {
    // The block lets a script declare its own `module`, `require`, ... like a top-level CommonJS file can.
    const body = new Function('require', 'process', 'console', 'module', 'exports', '__filename', '__dirname', `{\n${script}\n}`);
    const module = { exports: {} };
    body(requireFromRoot, fakeProcess, fakeConsole, module, module.exports, filename, root);
    await new Promise(resolve => setImmediate(resolve));
  } catch (error) {
    if (error instanceof ExitSignal) code = error.code;
    else { stderr += `${error && error.stack ? error.stack : String(error)}\n`; code = 1; }
  }
  for (const name of Object.getOwnPropertyNames(globalThis)) if (!baselineGlobals.has(name)) delete globalThis[name];
  return { code, stdout, stderr };
}

let queue = Promise.resolve();
readline.createInterface({ input: process.stdin, crlfDelay: Infinity }).on('line', line => {
  queue = queue.then(async () => reply(`${JSON.stringify(await runScript(JSON.parse(line).script))}\n`));
});
process.on('unhandledRejection', error => { process.stderr.write(`node_worker: ${error && error.stack || error}\n`); });
