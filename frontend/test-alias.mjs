import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log("Test de résolution d'alias @/");
console.log("Répertoire courant:", process.cwd());
console.log("__dirname:", __dirname);
console.log("Résolution de @/lib/utils:", path.resolve(__dirname, 'src/lib/utils'));
console.log("Existe?", fs.existsSync(path.resolve(__dirname, 'src/lib/utils.ts')));
