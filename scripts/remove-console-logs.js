#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

/**
 * Production Console.log Removal Tool
 * 本番環境向けconsole.log削除ツール
 */

const COLORS = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  reset: '\x1b[0m'
};

const log = {
  info: (msg) => console.log(`${COLORS.blue}[INFO]${COLORS.reset} ${msg}`),
  success: (msg) => console.log(`${COLORS.green}[SUCCESS]${COLORS.reset} ${msg}`),
  warning: (msg) => console.log(`${COLORS.yellow}[WARNING]${COLORS.reset} ${msg}`),
  error: (msg) => console.log(`${COLORS.red}[ERROR]${COLORS.reset} ${msg}`)
};

class ConsoleLogRemover {
  constructor(basePath = './miraikakakufront') {
    this.basePath = basePath;
    this.stats = {
      filesProcessed: 0,
      consoleLogsRemoved: 0,
      errorsRemoved: 0,
      warnsRemoved: 0,
      debugsRemoved: 0
    };
  }

  async findFiles(dir, extensions = ['.ts', '.tsx', '.js', '.jsx']) {
    const files = [];

    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory() && entry.name !== 'node_modules' && !entry.name.startsWith('.')) {
          files.push(...await this.findFiles(fullPath, extensions));
        } else if (entry.isFile() && extensions.some(ext => entry.name.endsWith(ext))) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      log.error(`Error reading directory ${dir}: ${error.message}`);
    }

    return files;
  }

  async processFile(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      let modifiedContent = content;
      let removedCount = 0;

      // Console.log patterns to remove
      const patterns = [
        // console.log(...) - single line and multiline
        {
          regex: /console\.log\s*\([^)]*(?:\([^)]*\)[^)]*)*\)\s*;?\s*\n?/g,
          type: 'log'
        },
        // console.error(...) - be more careful with errors
        {
          regex: /console\.error\s*\([^)]*(?:\([^)]*\)[^)]*)*\)\s*;?\s*\n?/g,
          type: 'error'
        },
        // console.warn(...)
        {
          regex: /console\.warn\s*\([^)]*(?:\([^)]*\)[^)]*)*\)\s*;?\s*\n?/g,
          type: 'warn'
        },
        // console.debug(...)
        {
          regex: /console\.debug\s*\([^)]*(?:\([^)]*\)[^)]*)*\)\s*;?\s*\n?/g,
          type: 'debug'
        }
      ];

      for (const pattern of patterns) {
        const matches = modifiedContent.match(pattern.regex);
        if (matches) {
          const count = matches.length;
          modifiedContent = modifiedContent.replace(pattern.regex, '');
          removedCount += count;
          this.stats[`${pattern.type}sRemoved`] = (this.stats[`${pattern.type}sRemoved`] || 0) + count;
        }
      }

      if (removedCount > 0) {
        // Clean up extra empty lines left by console.log removal
        modifiedContent = modifiedContent.replace(/\n\s*\n\s*\n/g, '\n\n');
        await fs.writeFile(filePath, modifiedContent, 'utf-8');

        log.info(`${filePath}: Removed ${removedCount} console statements`);
        this.stats.consoleLogsRemoved += removedCount;
      }

      this.stats.filesProcessed++;

    } catch (error) {
      log.error(`Error processing ${filePath}: ${error.message}`);
    }
  }

  async run() {
    log.info(`Starting console.log removal in ${this.basePath}`);

    const files = await this.findFiles(this.basePath);
    log.info(`Found ${files.length} files to process`);

    for (const file of files) {
      await this.processFile(file);
    }

    this.printStats();
  }

  printStats() {
    console.log('\n' + '='.repeat(50));
    log.success('Console.log Removal Complete');
    console.log('='.repeat(50));
    console.log(`Files Processed: ${this.stats.filesProcessed}`);
    console.log(`Total Console Statements Removed: ${this.stats.consoleLogsRemoved}`);
    console.log(`  - console.log: ${this.stats.logsRemoved || 0}`);
    console.log(`  - console.error: ${this.stats.errorsRemoved || 0}`);
    console.log(`  - console.warn: ${this.stats.warnsRemoved || 0}`);
    console.log(`  - console.debug: ${this.stats.debugsRemoved || 0}`);
    console.log('='.repeat(50) + '\n');
  }
}

// Run if called directly
if (require.main === module) {
  const remover = new ConsoleLogRemover();
  remover.run().catch(error => {
    log.error(`Script failed: ${error.message}`);
    process.exit(1);
  });
}

module.exports = ConsoleLogRemover;