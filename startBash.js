"use strict";

const join = require("path").join;
const execSync = require("child_process").execSync;
const env = require("process").env;

const setupCommand = "bash " + join(__dirname, "setup.sh")
const runCommand = "sh " + join(__dirname, "action.sh")

execSync(setupCommand, {"cwd":__dirname, "stdio":"inherit"});
//execSync(runCommand, {"cwd": env.GITHUB_WORKSPACE, "stdio":"inherit"});
execSync(runCommand, {"stdio":"inherit"});
