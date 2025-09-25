#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

/**
 * Final Syntax Fix Tool
 * 特定の構文エラーパターンを修正
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

class FinalSyntaxFixer {
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

      // Pattern 1: Fix missing closing parentheses in function calls
      const patterns = [
        // useState<Type>(value  ->  useState<Type>(value)
        { from: /useState<[^>]+>\([^)]*$\n/gm, to: (match) => match.trim() + ')\n', desc: 'useState closing parens' },
        // useRouter(  ->  useRouter()
        { from: /useRouter\(\s*$/gm, to: 'useRouter()', desc: 'useRouter closing parens' },
        // useEffect(() => {  without closing
        { from: /useEffect\(\(\) => \{\s*$/gm, to: '', desc: 'incomplete useEffect' },

        // Pattern 2: Fix object/array syntax
        // subsets: ["latin"]  ->  subsets: ["latin"],
        { from: /subsets:\s*\["latin"\]\s*\n/g, to: 'subsets: ["latin"],\n', desc: 'subsets comma' },
        // display: 'swap'  ->  display: 'swap',
        { from: /display:\s*'swap'\s*\n/g, to: "display: 'swap',\n", desc: 'display comma' },

        // Pattern 3: Fix missing function call endings
        // checkAuthentication(  ->  checkAuthentication()
        { from: /(\w+)\(\s*$/gm, to: '$1()', desc: 'function call endings' }
      ];

      for (const pattern of patterns) {
        const before = content;
        if (typeof pattern.to === 'function') {
          content = content.replace(pattern.from, pattern.to);
        } else {
          content = content.replace(pattern.from, pattern.to);
        }
        if (content !== before) {
          fixes++;
          log.info(`  Fixed ${pattern.desc} in ${filePath}`);
        }
      }

      // Specific file-based fixes
      if (filePath.includes('layout.tsx')) {
        // Fix Inter font configuration
        content = content.replace(
          /const inter = Inter\(\{\s*subsets:\s*\["latin"\]\s*display:\s*'swap'\s*\}/g,
          "const inter = Inter({\n  subsets: ['latin'],\n  display: 'swap'\n})"
        );
      }

      if (content !== originalContent) {
        await fs.writeFile(filePath, content, 'utf-8');
        log.success(`${filePath}: Fixed ${fixes} syntax issues`);
        this.fixCount += fixes;
      }

    } catch (error) {
      log.error(`Error processing ${filePath}: ${error.message}`);
    }
  }

  async run() {
    log.info(`Starting final syntax fixes in ${this.basePath}`);

    const files = await this.findFiles(this.basePath);
    log.info(`Found ${files.length} files to process`);

    for (const file of files) {
      await this.fixFile(file);
    }

    this.printStats();
  }

  printStats() {
    console.log('\n' + '='.repeat(50));
    log.success('Final Syntax Fixes Complete');
    console.log('='.repeat(50));
    console.log(`Total Fixes Applied: ${this.fixCount}`);
    console.log('='.repeat(50) + '\n');
  }
}

// Run if called directly
if (require.main === module) {
  const fixer = new FinalSyntaxFixer();
  fixer.run().catch(error => {
    log.error(`Script failed: ${error.message}`);
    process.exit(1);
  });
}

module.exports = FinalSyntaxFixer;