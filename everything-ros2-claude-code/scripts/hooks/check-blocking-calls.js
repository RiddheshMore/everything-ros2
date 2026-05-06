#!/usr/bin/env node
/**
 * Hook: Detect blocking calls inside ROS 2 callback methods.
 * time.sleep() inside a callback starves the executor.
 */

const fs = require('fs');
const path = require('path');

const filePath = process.argv[2];
if (!filePath || !fs.existsSync(filePath)) process.exit(0);

const content = fs.readFileSync(filePath, 'utf8');
const lines = content.split('\n');

// Simple heuristic: detect time.sleep inside _callback methods
let insideCallback = false;
let callbackIndent = 0;
let found = false;

lines.forEach((line, i) => {
  const stripped = line.trim();
  const indent = line.search(/\S/);

  // Detect callback method definitions
  if (/def\s+\w*(callback|_cb|_timer|_subscriber)\w*\s*\(/.test(stripped)) {
    insideCallback = true;
    callbackIndent = indent;
    return;
  }

  // Reset when indent returns to method level
  if (insideCallback && stripped !== '' && indent <= callbackIndent && !stripped.startsWith('#')) {
    if (!/^def\s/.test(stripped) === false) {
      insideCallback = false;
    }
    if (indent < callbackIndent) {
      insideCallback = false;
    }
  }

  if (insideCallback) {
    if (/time\.sleep\s*\(/.test(stripped)) {
      if (!found) {
        process.stderr.write(`\n[ROS 2 Hook] ⚠️  Blocking call in callback in ${path.basename(filePath)}:\n`);
        found = true;
      }
      process.stderr.write(`  Line ${i + 1}: time.sleep() inside callback blocks the executor!\n`);
      process.stderr.write(`            Fix: use self.create_timer() with a separate callback instead.\n`);
    }
    if (/rclpy\.spin_until_future_complete\(self/.test(stripped)) {
      if (!found) {
        process.stderr.write(`\n[ROS 2 Hook] ⚠️  Potential deadlock in ${path.basename(filePath)}:\n`);
        found = true;
      }
      process.stderr.write(`  Line ${i + 1}: spin_until_future_complete(self, ...) inside a callback can deadlock!\n`);
      process.stderr.write(`            Fix: use future.add_done_callback() or MultiThreadedExecutor with separate callback groups.\n`);
    }
  }
});

process.exit(0);
