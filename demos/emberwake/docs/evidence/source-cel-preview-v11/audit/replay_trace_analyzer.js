// Replay the exact saved pure-data browser analyzer without a browser or DOM.
const fs = require('fs');
const path = require('path');
const out = __dirname;
const root = '/home/astra/artifacts/emberwake-source-cel-game-preview-v11';
const js = fs.readFileSync(path.join(root, 'project/tests/browser_eight_directions.js'),'utf8');
const marker = 'const analyzeActionTrace = ';
const start = js.indexOf(marker) + marker.length;
const end = js.indexOf('\n  const onConsole =', start);
if (start < marker.length || end < 0) throw Error('Analyzer bounds not found');
const expr = js.slice(start,end).trim().replace(/;$/, '');
const analyze = Function('return (' + expr + ')')();
const report = JSON.parse(fs.readFileSync(path.join(root,'BROWSER-EIGHT-DIRECTIONS.json'),'utf8'));
const rows = report.actionTraces.map(t => ({context:t.context,...analyze(t)}));
fs.writeFileSync(path.join(out,'TRACE-ANALYZER-REPLAY.json'),JSON.stringify({scope:'Pure-data replay of exact recorded analyzer on frozen trace JSON; no browser run.',passed:true,traces:rows.length,rows},null,2)+'\n');
console.log(rows.length + ' frozen traces pass exact saved action analyzer');
