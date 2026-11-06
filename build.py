#!/usr/bin/env python3
"""Build this patch from pinned inputs (see README.md, BUILDING.md, NOTES.md). The decisions are in records.json:
each record starts from `base` and takes named fields from a donor plugin.
Usage: python3 build.py          (serializes inputs/, prints the records, writes no plugin)
       python3 build.py --write  (also writes dist/, then round-trips and parses the result)
Needs: dotnet, python3, the Spriggit.Yaml.Skyrim 0.41.0 DLL (SPRIGGIT_DLL or auto-detected), inputs/ (BUILDING.md)."""
import hashlib, json, os, pathlib, re, shutil, struct, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
INPUTS = pathlib.Path(os.environ.get('INPUTS', HERE / 'inputs'))
Y = HERE / 'build'
PATCH = json.loads((HERE / 'records.json').read_text())
NAME = PATCH['name']


def find_dll():  # SPRIGGIT_DLL, else Spriggit's own download folder, else the NuGet cache
    if os.environ.get('SPRIGGIT_DLL'):
        return pathlib.Path(os.environ['SPRIGGIT_DLL'])
    for base in [pathlib.Path(d) / 'Spriggit/Translations/Spriggit.Yaml.Skyrim/0.41.0'
                 for d in {os.environ.get('TMPDIR', ''), tempfile.gettempdir(), '/tmp'} if d] + [
            pathlib.Path.home() / '.nuget/packages/spriggit.yaml.skyrim/0.41.0']:
        hits = sorted(base.rglob('Spriggit.Yaml.Skyrim.dll')) if base.is_dir() else []
        if hits:
            return hits[0]
    sys.exit('Spriggit.Yaml.Skyrim.dll 0.41.0 not found. See BUILDING.md, or set SPRIGGIT_DLL.')


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-800:] + r.stderr[-800:])


def spriggit(dll, verb, src, dst, *more):
    run(['dotnet', str(dll), verb, '-i', str(src), '-o', str(dst), *more])


def check_inputs():  # refuse anything but the versions this patch was written for
    for line in (HERE / 'inputs.sha256').read_text().splitlines():
        want, name = line.split(None, 1)
        f = INPUTS / name
        if not f.is_file():
            sys.exit(f'missing input: {name} (see BUILDING.md)')
        if hashlib.sha256(f.read_bytes()).hexdigest() != want:
            sys.exit(f'{name} differs from the version this patch was written for (see BUILDING.md)')


def blocks(text):  # top-level keys -> lines; Spriggit writes a top-level list's items at column 0
    out, key = {}, None
    for l in text.splitlines():
        if l and not l[0].isspace() and not l.startswith('- '):
            key = l.split(':')[0]
            out[key] = []
        out[key].append(l)
    return out


def overlay(base, src, take):  # base with `take` fields replaced by src's (added or dropped as src has them)
    keys = list(base)
    for i, k in enumerate(src):
        if k in take and k not in base:
            prev = [x for x in list(src)[:i] if x in keys]
            keys.insert(keys.index(prev[-1]) + 1 if prev else len(keys), k)
    return {k: (src[k] if k in take else base[k]) for k in keys if not (k in take and k not in src)}


def scripts(b):  # VMAD -> (lines before the first script, {name: its lines})
    head, sc, cur = [], {}, None
    for l in b.get('VirtualMachineAdapter', []):
        m = re.match(r'  - Name: (.+)$', l)
        if m:
            cur = m.group(1)
            sc[cur] = []
        (sc[cur] if cur else head).append(l)
    return head, sc


def merge_scripts(cur, src, step):
    head, sc = scripts(cur)
    dh, ds = scripts(src)
    head = head or dh
    for x in step.get('drop_scripts', []):
        del sc[x]
    for x in step['add_scripts']:
        sc[x] = ds[x]
    vm = head + [l for v in sc.values() for l in v]
    if 'VirtualMachineAdapter' in cur:
        return {**cur, 'VirtualMachineAdapter': vm}
    keys = list(cur)
    cut = keys.index('EditorID') + 1  # Spriggit writes VMAD straight after the version fields
    return {**{k: cur[k] for k in keys[:cut]}, 'VirtualMachineAdapter': vm, **{k: cur[k] for k in keys[cut:]}}


def record_file(plugin, r):
    if r.get('path'):
        return Y / f'yaml-{plugin[:-4]}' / r['path']
    idn, origin = r['form'].split(':', 1)
    end = f' - {idn}_{origin}.yaml'.lower()
    hits = [f for f in (Y / f'yaml-{plugin[:-4]}' / r['sub']).glob('*.yaml') if f.name.lower().endswith(end)]
    assert len(hits) == 1, (plugin, r['form'], len(hits))
    return hits[0]


def merged(r):
    f = record_file(r['base'], r)
    cur = blocks(f.read_text())
    for step in r['steps']:
        src = blocks(record_file(step['donor'], r).read_text())
        if 'add_scripts' in step:
            cur = merge_scripts(cur, src, step)
            continue
        have = cur.get('Keywords', ['Keywords:'])
        cur = overlay(cur, src, set(step['take']))
        if step.get('add_keywords'):
            cur['Keywords'] = have + step['add_keywords']
    for k in r.get('drop', []):
        cur.pop(k, None)
    rel = r.get('path') or f"{r['sub']}/{f.name}"
    return rel, ''.join(l + '\n' for v in cur.values() for l in v)


def main():
    write = '--write' in sys.argv
    check_inputs()
    dll = find_dll()
    shutil.rmtree(Y, ignore_errors=True)
    for p in PATCH['inputs']:
        spriggit(dll, 'serialize', INPUTS / p, Y / f'yaml-{p[:-4]}', '-g', 'SkyrimSE', '-p', 'Spriggit.Yaml.Skyrim', '-v', '0.41.0')
    recs = dict(merged(r) for r in PATCH['records'])
    print(f'{NAME}: {len(recs)} records, {len(PATCH["masters"])} masters')
    if not write:
        return
    out, rt, esp = Y / 'out', Y / 'rt', HERE / 'dist' / f'{NAME}.esp'
    for rel, t in recs.items():
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_text(t)
    refs = ''.join(f'  - Master: {m}\n    FileSize: 0\n' for m in PATCH['masters'])
    (out / 'RecordData.yaml').write_text(
        'SpriggitSource:\n  PackageName: Spriggit.Yaml.Skyrim\n  Version: 0.41.0\n'
        f'ModKey: {NAME}.esp\nGameRelease: SkyrimSE\nModHeader:\n  Flags:\n  - Small\n'
        '  Stats:\n    Version: 1.7\n    NextFormID: 2048\n  Author: kxgcayh\n'
        f'  Description: {PATCH["description"]}\n  MasterReferences:\n{refs}  INTV: 1\n')
    esp.parent.mkdir(exist_ok=True)
    spriggit(dll, 'deserialize', out, esp)
    spriggit(dll, 'serialize', esp, rt, '-g', 'SkyrimSE', '-p', 'Spriggit.Yaml.Skyrim', '-v', '0.41.0')
    for rel, t in recs.items():  # lower(): the header's master casing replaces the casing in the FormKeys
        assert sorted(t.lower().splitlines()) == sorted((rt / rel).read_text().lower().splitlines()), f'round trip differs: {rel}'
    check_plugin(esp.read_bytes(), len(recs))
    print('wrote', esp)


def check_plugin(b, want):  # independent of Spriggit: ESL flag, masters, record count, no new forms
    assert struct.unpack_from('<I', b, 8)[0] & 0x200, 'ESL flag missing'
    size = struct.unpack_from('<I', b, 4)[0]
    h, i, ms = b[24:24 + size], 0, []
    while i + 6 <= len(h):
        t, n = h[i:i + 4], struct.unpack_from('<H', h, i + 4)[0]
        if t == b'MAST':
            ms.append(h[i + 6:i + 6 + n].rstrip(b'\0').decode('latin1'))
        i += 6 + n
    assert ms == PATCH['masters'], 'masters changed'
    off, n = 24 + size, 0
    while off < len(b):
        t, sz, _, fid = struct.unpack_from('<4sIII', b, off)
        if t == b'GRUP':
            off += 24
            continue
        assert fid >> 24 < len(ms), f'new form {fid:08X}'
        n += 1
        off += 24 + sz
    assert n == want, (n, want)


if __name__ == '__main__':
    main()
