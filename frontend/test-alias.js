import path from 'path';

console.log("Test de résolution d'alias @/");
console.log("Répertoire courant:", process.cwd());
console.log("__dirname:", __dirname);
console.log("Résolution de @/lib/utils:", path.resolve(__dirname, 'src/lib/utils'));
console.log("Existe?", require('fs').existsSync(path.resolve(__dirname, 'src/lib/utils.ts')));
