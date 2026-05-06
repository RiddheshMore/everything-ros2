#!/usr/bin/env node
/**
 * Hook: Validate URDF/XACRO on save.
 * Runs check_urdf if available; warns but does not block.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const filePath = process.argv[2];
if (!filePath || !fs.existsSync(filePath)) process.exit(0);

const ext = path.extname(filePath);
if (ext !== '.urdf' && ext !== '.xacro') process.exit(0);

// Check if check_urdf is available
try {
  execSync('which check_urdf', { stdio: 'ignore' });
} catch {
  // check_urdf not available — skip silently
  process.exit(0);
}

process.stderr.write(`[ROS 2 Hook] Validating URDF: ${path.basename(filePath)}\n`);

let urdfPath = filePath;

// Expand XACRO first
if (ext === '.xacro') {
  try {
    execSync('which xacro', { stdio: 'ignore' });
    const tmpPath = `/tmp/ros2_hook_expanded_${Date.now()}.urdf`;
    execSync(`xacro "${filePath}" > "${tmpPath}" 2>&1`);
    urdfPath = tmpPath;
  } catch (e) {
    process.stderr.write(`[ROS 2 Hook] xacro not found or failed to expand. Skipping validation.\n`);
    process.exit(0);
  }
}

// Run check_urdf
try {
  const result = execSync(`check_urdf "${urdfPath}" 2>&1`, { encoding: 'utf8' });
  process.stderr.write(`[ROS 2 Hook] ✅ URDF valid: ${result.split('\n')[0]}\n`);
} catch (e) {
  process.stderr.write(`[ROS 2 Hook] ❌ URDF validation FAILED:\n`);
  process.stderr.write(e.stdout || e.message);
  process.stderr.write(`\nRun /urdf-check for detailed diagnosis.\n\n`);
}

process.exit(0); // Never block on URDF errors — just warn
