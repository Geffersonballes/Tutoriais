"""Renderizador do PC do dono (GPU GTX 1660 Super). Roda sozinho num terminal:
    python render_fila/worker.py
Fica olhando render_fila/pendente/ na branch, pega o pedido mais antigo, renderiza TODOS os quadros
a 30 FPS em 1080x1920 (EEVEE na GPU), monta o final.mp4 com o compor.py, sobe no Picsart e grava
render_fila/pronto/<pedido>.json com a URL. As sessões da nuvem leem o "pronto" e agendam.

Pedido (render_fila/pendente/<id>.json):
  {"pasta": "serie-games/producao/2026-11-29_x", "cena": "tiktok-geopolitica/motor/cena_x.py",
   "env": {"REALISTA": "1"}, "sessao": "games", "criado": "2026-11-29T09:40"}
Tudo o que a cena e o compor precisam (narracao.mp3, legendas.json, palavras.json, grafismos.json,
curtir.mp3 se houver, capa) tem que estar commitado na pasta. frames/ e final.mp4 não vão para o git."""
import json, os, sys, time, glob, shutil, subprocess, socket, datetime, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "claude/nifty-noether-jtt32a"
BLENDER = os.environ.get("BLENDER") or next((p for p in sorted(glob.glob(r"C:\Render\blender-4.2*\blender.exe") + glob.glob(r"C:\Render\blender-4.2*\*\blender.exe")) + [
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender\blender.exe",
    r"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe",
    r"C:\Program Files\Steam\steamapps\common\Blender\blender.exe", shutil.which("blender") or ""] if p and os.path.exists(p)), "blender")
NOME = socket.gethostname()
PY = sys.executable

def sh(cmd, **kw):
    print("  $", " ".join(cmd) if isinstance(cmd, list) else cmd, flush=True)
    return subprocess.run(cmd, cwd=RAIZ, **kw)

def git_sync():
    sh(["git", "fetch", "-q", "origin", BRANCH]); sh(["git", "merge", "-q", "--no-edit", "FETCH_HEAD"])

def git_push(msg, arquivos):
    sh(["git", "add", "-A"] + arquivos); sh(["git", "commit", "-q", "-m", msg])
    for _ in range(4):
        if sh(["git", "push", "-q", "origin", "HEAD:" + BRANCH]).returncode == 0: return True
        git_sync(); time.sleep(5)
    return False

def agora(): return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def pegar():
    git_sync()
    for p in sorted(glob.glob(os.path.join(RAIZ, "render_fila", "pendente", "*.json")), key=os.path.getmtime):
        job_id = os.path.splitext(os.path.basename(p))[0]
        job = json.load(open(p, encoding="utf-8")); job["worker"] = NOME; job["inicio"] = agora()
        dst = os.path.join(RAIZ, "render_fila", "em_andamento", job_id + ".json")
        json.dump(job, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1); os.remove(p)
        if git_push(f"render: {NOME} pegou {job_id}", ["render_fila"]): return job_id, job
        git_sync()   # outra máquina pegou antes
    return None, None

def render(job):
    pasta = os.path.join(RAIZ, job["pasta"]); cena = os.path.join(RAIZ, job["cena"])
    env = dict(os.environ, RES="1080", PASSO="1", **{k: str(v) for k, v in job.get("env", {}).items()})
    pr = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", cena, "--", pasta], cwd=RAIZ, env=env,
                        capture_output=True, text=True, errors="ignore")
    saida = (pr.stdout or "") + (pr.stderr or "")
    open(os.path.join(pasta, "render_pc_probe.log"), "w", encoding="utf-8").write(saida)
    m = re.search(r"FRAMES (\d+)", saida)
    if not m: raise RuntimeError("a cena nao informou FRAMES. Fim do log: " + saida[-1500:])
    n = int(m.group(1))
    shutil.rmtree(os.path.join(pasta, "frames"), ignore_errors=True)
    t0 = time.time()
    with open(os.path.join(pasta, "render_pc.log"), "w") as log:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", cena, "--", pasta, "range", f"1,{n}"],
                           cwd=RAIZ, env=env, stdout=log, stderr=subprocess.STDOUT)
    if r.returncode != 0: raise RuntimeError("blender falhou (veja render_pc.log)")
    t_render = time.time() - t0
    r = subprocess.run([PY, os.path.join(RAIZ, "tiktok-geopolitica", "motor", "compor.py"), pasta, os.path.join(pasta, "grafismos.json")], cwd=RAIZ)
    if r.returncode != 0: raise RuntimeError("compor falhou")
    final = os.path.join(pasta, "final.mp4")
    out = subprocess.run(["curl", "-sS", "--fail-with-body", "-F", "file=@" + final + ";type=video/mp4", "-F", "type=picsart-mcp",
                          "https://upload.picsart.com/v2/files"], capture_output=True, text=True).stdout
    url = json.loads(out)["response"]["url"]
    return {"url": url, "quadros": n, "min_render": round(t_render / 60, 1)}

def main():
    ver = subprocess.run([BLENDER, "-b", "--version"], capture_output=True, text=True, errors="ignore").stdout.splitlines()[:1]
    print(f"Renderizador {NOME} | {ver} | Blender: {BLENDER} | repo: {RAIZ}", flush=True)
    while True:
        try:
            job_id, job = pegar()
            if not job_id: time.sleep(60); continue
            print(f"\n== {agora()} renderizando {job_id}: {job['pasta']}", flush=True)
            try: res = render(job); job.update(res, fim=agora(), status="ok")
            except Exception as e: job.update(fim=agora(), status="erro", erro=str(e)[-1500:]); print("ERRO:", e, flush=True)
            os.remove(os.path.join(RAIZ, "render_fila", "em_andamento", job_id + ".json"))
            json.dump(job, open(os.path.join(RAIZ, "render_fila", "pronto", job_id + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            git_push(f"render: {job_id} {job['status']}", ["render_fila", os.path.join(job["pasta"], "capa.jpg")] if os.path.exists(os.path.join(RAIZ, job["pasta"], "capa.jpg")) else ["render_fila"])
            print(f"== {job_id}: {job['status']} {job.get('url','')}", flush=True)
        except KeyboardInterrupt: break
        except Exception as e: print("falha no ciclo:", e, flush=True); time.sleep(60)

if __name__ == "__main__": main()
