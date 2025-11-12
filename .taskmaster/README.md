# TaskMaster Configuration

This directory contains the local TaskMaster AI configuration for this project.

## Directory Structure

- `config.json` - Main configuration file
- `tasks/` - Task definitions and history
- `logs/` - Task execution logs

## Usage

TaskMaster AI is installed as a project dependency. You can:

1. Run via npx: `npx task-master-ai`
2. Use through Claude Code MCP integration
3. Import in your scripts: `require('task-master-ai')`

## Configuration

The `config.json` file references the `OPENAI_API_KEY` from your `.env` file.
Make sure your `.env` file is properly configured with your OpenAI API key.

## Learn More

- [TaskMaster AI Documentation](https://github.com/eyaltoledano/claude-task-master)
- [NPM Package](https://www.npmjs.com/package/task-master-ai)
