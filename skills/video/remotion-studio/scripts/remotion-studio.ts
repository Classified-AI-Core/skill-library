#!/usr/bin/env bun
import {existsSync} from 'node:fs';
import {spawn} from 'node:child_process';
import path from 'node:path';

type Command = 'init' | 'check' | 'dev' | 'studio' | 'render' | 'still' | 'help';

type Args = {
  command: Command;
  project?: string;
  composition?: string;
  out?: string;
  frame?: string;
};

const parseArgs = (argv: string[]): Args => {
  const [rawCommand, ...rest] = argv;
  const command = (rawCommand as Command) || 'help';
  const out: Args = {command};
  for (let i = 0; i < rest.length; i++) {
    const key = rest[i];
    const value = rest[i + 1];
    if (key === '--project') {
      out.project = value;
      i++;
    } else if (key === '--composition') {
      out.composition = value;
      i++;
    } else if (key === '--out') {
      out.out = value;
      i++;
    } else if (key === '--frame') {
      out.frame = value;
      i++;
    }
  }
  return out;
};

const help = () => {
  console.log(`remotion-studio

Usage:
  bun remotion-studio.ts <command> [flags]

Commands:
  init      Install required deps in a project
  check     Validate project structure and deps
  dev       Run Vite frontend for custom editor UI
  studio    Run Remotion Studio
  render    Render a composition to video
  still     Render a still frame

Flags:
  --project <absolute-path>    Project path (required for all commands except help)
  --composition <id>           Composition ID (render/still)
  --out <path>                 Output file path (render/still)
  --frame <number>             Frame number (still)
`);
};

const run = (cmd: string, args: string[], cwd: string) => {
  return new Promise<void>((resolve, reject) => {
    const child = spawn(cmd, args, {cwd, stdio: 'inherit', shell: false});
    child.on('exit', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${cmd} ${args.join(' ')} failed with code ${code}`));
    });
  });
};

const requireProject = (project?: string) => {
  if (!project) throw new Error('Missing --project');
  const resolved = path.resolve(project);
  if (!existsSync(resolved)) throw new Error(`Project not found: ${resolved}`);
  return resolved;
};

const fileRequired = (project: string, rel: string) => {
  const full = path.join(project, rel);
  if (!existsSync(full)) throw new Error(`Missing required file: ${full}`);
};

const main = async () => {
  const args = parseArgs(process.argv.slice(2));
  if (args.command === 'help' || !args.command) {
    help();
    return;
  }

  const project = requireProject(args.project);

  if (args.command === 'init') {
    await run('npm', ['install'], project);
    await run('npm', ['install', '-D', '@remotion/cli'], project);
    return;
  }

  if (args.command === 'check') {
    fileRequired(project, 'package.json');
    fileRequired(project, 'src/index.ts');
    fileRequired(project, 'src/remotion-root.tsx');
    fileRequired(project, 'remotion.config.ts');
    console.log('✅ Remotion project structure looks good.');
    return;
  }

  if (args.command === 'dev') {
    await run('npm', ['run', 'dev'], project);
    return;
  }

  if (args.command === 'studio') {
    await run('npm', ['run', 'remotion:studio'], project);
    return;
  }

  if (args.command === 'render') {
    const composition = args.composition || 'DemoVideo';
    const out = args.out || 'out/demo.mp4';
    await run('npx', ['remotion', 'render', 'src/index.ts', composition, out], project);
    return;
  }

  if (args.command === 'still') {
    const composition = args.composition || 'DemoVideo';
    const out = args.out || 'out/frame.png';
    const frame = args.frame || '0';
    await run('npx', ['remotion', 'still', 'src/index.ts', composition, out, '--frame', frame], project);
    return;
  }

  help();
};

main().catch((err) => {
  console.error(`❌ ${err.message}`);
  process.exit(1);
});
