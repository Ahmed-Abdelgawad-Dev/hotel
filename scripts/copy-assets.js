const fs = require('fs');
const path = require('path');

const STATIC_DIR = path.join(__dirname, '../hotel/static');

// Ensure directories exist
const dirs = ['js', 'css', 'fonts'];
dirs.forEach(dir => {
  const dirPath = path.join(STATIC_DIR, dir);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
});

console.log('Copying assets to static directory...');

// Copy Alpine.js
const alpineSrc = path.join(__dirname, '../node_modules/alpinejs/dist/cdn.min.js');
const alpineDest = path.join(STATIC_DIR, 'js/alpine.min.js');
if (fs.existsSync(alpineSrc)) {
  fs.copyFileSync(alpineSrc, alpineDest);
  console.log('✓ Alpine.js copied');
} else {
  console.log('✗ Alpine.js not found');
}

// Copy Zod
const zodSrc = path.join(__dirname, '../node_modules/zod/lib/index.umd.js');
const zodDest = path.join(STATIC_DIR, 'js/zod.min.js');
if (fs.existsSync(zodSrc)) {
  fs.copyFileSync(zodSrc, zodDest);
  console.log('✓ Zod copied');
} else {
  console.log('✗ Zod not found');
}

console.log('\nAssets copied successfully!');
console.log('\nNext steps:');
console.log('1. Run: npm run build');
console.log('2. This will generate the Tailwind CSS file');
