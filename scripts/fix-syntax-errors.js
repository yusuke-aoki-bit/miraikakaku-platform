#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

/**
 * Syntax Error Fix Tool
 * console.log削除で発生した構文エラーを修正
 */

const COLORS = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

const log = {
  info: (msg) => console.log(`${COLORS.blue}[INFO]${COLORS.reset} ${msg}`),
  success: (msg) => console.log(`${COLORS.green}[SUCCESS]${COLORS.reset} ${msg}`),
  warning: (msg) => console.log(`${COLORS.yellow}[WARNING]${COLORS.reset} ${msg}`),
  error: (msg) => console.log(`${COLORS.red}[ERROR]${COLORS.reset} ${msg}`)
};

class SyntaxErrorFixer {
  constructor(basePath = './miraikakakufront') {
    this.basePath = basePath;
    this.fixCount = 0;
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

  async fixFile(filePath) {
    try {
      let content = await fs.readFile(filePath, 'utf-8');
      const originalContent = content;
      let fixes = 0;

      // Fix patterns caused by console.log removal
      const patterns = [
        // Fix dangling ");", ":", "," patterns
        { from: /\s*\);\s*\n/g, to: '\n', desc: 'dangling );' },
        { from: /\s*:\s*\n/g, to: '\n', desc: 'dangling :' },
        { from: /\s*,\s*\n/g, to: '\n', desc: 'dangling ,' },
        { from: /\s*,\s*\}/g, to: '\n}', desc: 'comma before }' },
        { from: /\s*,\s*\]/g, to: '\n]', desc: 'comma before ]' },

        // Fix empty lines and spacing
        { from: /\n\s*\n\s*\n\s*\n/g, to: '\n\n', desc: 'excessive empty lines' },
        { from: /\n\s*\n\s*\n/g, to: '\n\n', desc: 'double empty lines' },

        // Fix specific bad patterns
        { from: /\s*\?\s*[^:]*:\s*\n/g, to: '\n', desc: 'incomplete ternary' },
        { from: /\s*\?\s*\n/g, to: '\n', desc: 'dangling ?' },
        { from: /\s*:\s*`[^`]*`,?\s*\n/g, to: '\n', desc: 'template literal fragments' }
      ];

      for (const pattern of patterns) {
        const matches = content.match(pattern.from);
        if (matches) {
          content = content.replace(pattern.from, pattern.to);
          fixes += matches.length;
          log.info(`  Fixed ${matches.length} instances of ${pattern.desc}`);
        }
      }

      // Additional cleanup for specific syntax errors
      content = this.fixSpecificErrors(content, filePath);

      if (content !== originalContent) {
        await fs.writeFile(filePath, content, 'utf-8');
        log.success(`${filePath}: Fixed ${fixes} syntax issues`);
        this.fixCount += fixes;
      }

    } catch (error) {
      log.error(`Error processing ${filePath}: ${error.message}`);
    }
  }

  fixSpecificErrors(content, filePath) {
    // Fix specific known patterns based on file type
    if (filePath.includes('api.ts')) {
      content = content.replace(/\s*:\s*`[^`]*`,?\s*errorMessage\);/g, '');
    }

    if (filePath.includes('RankingCard.tsx')) {
      content = content.replace(/\s*\);\s*return;/g, '\n          return;');
    }

    if (filePath.includes('StockChart.tsx')) {
      content = content.replace(/\s*,\s*length:\s*Array\.isArray\([^}]+\}/g, '');
    }

    return content;
  }

  async run() {
    log.info(`Starting syntax error fixes in ${this.basePath}`);

    const files = await this.findFiles(this.basePath);
    log.info(`Found ${files.length} files to process`);

    for (const file of files) {
      await this.fixFile(file);
    }

    this.printStats();
  }

  printStats() {
    console.log('\n' + '='.repeat(50));
    log.success('Syntax Error Fixes Complete');
    console.log('='.repeat(50));
    console.log(`Total Fixes Applied: ${this.fixCount}`);
    console.log('='.repeat(50) + '\n');
  }
}

// Run if called directly
if (require.main === module) {
  const fixer = new SyntaxErrorFixer();
  fixer.run().catch(error => {
    log.error(`Script failed: ${error.message}`);
    process.exit(1);
  });
}

module.exports = SyntaxErrorFixer;