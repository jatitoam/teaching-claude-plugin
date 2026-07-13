#!/usr/bin/env python3
"""
Lector de UN board de Miro para asistencia (course-factory plugin · skill attendance).

Capa LECTORA (read-only), compañera de `estampar.py` (miro-boards): estampar.py ESCRIBE la
grilla de ~40 frames por estudiante; este script LEE ese board completo vía la REST API v2 de
Miro y vuelca, por frame, su título + los ítems hijos con atribución de autoría, para que un
agente aguas abajo pueda: (1) emparejar cada frame con el roster de alumnos por el TÍTULO del
frame, (2) juzgar si el alumno agregó contenido real, y (3) atribuir la autoría del contenido
agregado. NUNCA escribe en Miro — solo GET.

Uso:
    export MIRO_TOKEN=...                              # token de la app (NO se guarda en el repo)
    python3 leer_tablero.py <board_id>                 # imprime el JSON completo a stdout
    python3 leer_tablero.py <board_id> --out salida.json   # escribe el JSON y un resumen corto

<board_id> es el id del board de Miro (el segmento final de la URL, p.ej. "uXjVH-3WFJk=" —
se pasa tal cual, incluyendo cualquier "=").

Contexto: los frames los crea el script de construcción del instructor (estampar.py), así que
el `createdBy` propio de un frame = la cuenta de servicio/instructor. Los alumnos RENOMBRAN el
título del frame a "<carné> - <nombre>" y AGREGAN sus propios sticky notes/textos adentro. Por
eso: el TÍTULO del frame es la afirmación (claim); los ítems hijos CREADOS por el alumno
(createdBy != cuenta de servicio) son la señal confiable de autoría.

El título por defecto (sin reclamar) del frame es "Carnet y Nombre"; también se tratan como
default/no reclamado las variantes "ID y Nombre" e "ID and Name".

Forma exacta del JSON de salida:
{
  "board_id": "...",
  "board_name": "...",
  "board_url": "...",
  "service_account_id": "<id o null>",
  "frames": [
    {
      "frame_id": "...",
      "title": "24001301 - Fabricio Galvez",
      "is_default_title": false,
      "created_by": "<id o null>",
      "created_by_name": "<nombre o null>",
      "modified_by": "<id o null>",          // última cuenta que modificó el frame (renombró el título) — prueba de autoría
      "modified_by_name": "<nombre o null>",
      "children": [
        {"item_id": "...", "type": "sticky_note", "content": "WhatsApp",
         "created_by_id": "<id o null>", "created_by_name": "<nombre o null>",
         "is_student_created": true}
      ]
    }
  ],
  "author_frame_counts": {"<author_id>": <int>},      // frames donde la cuenta creó contenido de alumno
  "modifier_frame_counts": {"<account_id>": <int>},   // frames que la cuenta modificó por última vez (≠ servicio)
  "members": {"<id>": "<nombre o null>"},
  "summary": {"frames_total": N, "frames_renamed": N, "frames_default": N, "children_total": N}
}
"""
import os, sys, json, re, html, time, argparse, urllib.request, urllib.error

TOKEN = os.environ.get("MIRO_TOKEN")
API = "https://api.miro.com"

DEFAULT_TITLES = {"Carnet y Nombre", "ID y Nombre", "ID and Name"}


def _req(method, path):
    if not TOKEN:
        sys.exit("ERROR: falta la variable de entorno MIRO_TOKEN (alerta al conductor).")
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    req = urllib.request.Request(API + path, headers=headers, method=method)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code == 401:
                sys.exit("ERROR 401 — token MIRO_TOKEN inválido o falta (alerta al conductor).")
            if e.code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(1 + attempt)
                continue
            sys.exit(f"ERROR HTTP {e.code} en {method} {path}: {msg}\n(alerta al conductor)")
        except Exception as ex:  # noqa
            if attempt < 4:
                time.sleep(1 + attempt)
                continue
            sys.exit(f"ERROR de red en {method} {path}: {ex}\n(alerta al conductor)")


def _paged(path_base):
    """GET paginado siguiendo el cursor de respuesta; devuelve la lista completa de `data`."""
    out = []
    cursor = None
    while True:
        path = path_base + (f"&cursor={cursor}" if cursor else "")
        resp = _req("GET", path)
        out.extend(resp.get("data", []))
        cursor = resp.get("cursor")
        if not cursor:
            break
    return out


def _author_id(item, field):
    v = item.get(field)
    if isinstance(v, dict):
        return v.get("id")
    return None


def _html_to_text(raw, limit=500):
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def leer(board_id):
    board = _req("GET", f"/v2/boards/{board_id}")
    board_name = board.get("name")
    board_url = board.get("viewLink") or f"https://miro.com/app/board/{board_id}"

    items = _paged(f"/v2/boards/{board_id}/items?limit=50")

    members_list = _paged(f"/v2/boards/{board_id}/members?limit=50")
    members = {}
    for m in members_list:
        mid = m.get("id")
        if mid is not None:
            name = m.get("name") or (m.get("user") or {}).get("name")
            members[mid] = name

    frames = {}
    children_by_parent = {}
    for it in items:
        iid = it.get("id")
        itype = it.get("type")
        data = it.get("data") or {}
        parent = it.get("parent") or {}
        parent_id = parent.get("id")
        created_by = _author_id(it, "createdBy")
        modified_by = _author_id(it, "modifiedBy")

        if itype == "frame":
            title = data.get("title") or ""
            frames[iid] = {
                "frame_id": iid,
                "title": title,
                "is_default_title": title in DEFAULT_TITLES,
                "created_by": created_by,
                "created_by_name": members.get(created_by),
                "modified_by": modified_by,           # última cuenta que modificó el frame (p.ej. renombró el título)
                "modified_by_name": members.get(modified_by),
                "children": [],
            }
        else:
            content = data.get("content") if "content" in data else data.get("title")
            children_by_parent.setdefault(parent_id, []).append({
                "item_id": iid,
                "type": itype,
                "content": _html_to_text(content),
                "created_by_id": created_by,
                "created_by_name": members.get(created_by),
                "is_student_created": None,  # se completa luego de conocer service_account_id
            })

    # service_account_id: el autor que más veces creó frames (moda)
    author_frame_counts_raw = {}
    for f in frames.values():
        cb = f["created_by"]
        if cb:
            author_frame_counts_raw[cb] = author_frame_counts_raw.get(cb, 0) + 1
    service_account_id = None
    if author_frame_counts_raw:
        service_account_id = max(author_frame_counts_raw, key=author_frame_counts_raw.get)

    for fid, f in frames.items():
        kids = children_by_parent.get(fid, [])
        for k in kids:
            cb = k["created_by_id"]
            k["is_student_created"] = cb is not None and cb != service_account_id
        f["children"] = kids

    # author_frame_counts: por autor, cantidad de frames DISTINTOS donde creó >=1 ítem de alumno
    author_frame_sets = {}
    for fid, f in frames.items():
        seen_authors_this_frame = set()
        for k in f["children"]:
            if k["is_student_created"]:
                cb = k["created_by_id"]
                if cb not in seen_authors_this_frame:
                    seen_authors_this_frame.add(cb)
                    author_frame_sets.setdefault(cb, set()).add(fid)
    author_frame_counts = {k: len(v) for k, v in author_frame_sets.items()}

    # modifier_frame_counts: por cuenta, nº de frames DISTINTOS que esa cuenta modificó por última
    # vez (excluye la cuenta de servicio). Señal de proxy complementaria a author_frame_counts:
    # una cuenta que editó/renombró muchos frames ajenos.
    modifier_frame_counts = {}
    for f in frames.values():
        mb = f.get("modified_by")
        if mb and mb != service_account_id:
            modifier_frame_counts[mb] = modifier_frame_counts.get(mb, 0) + 1

    frame_list = list(frames.values())
    frames_total = len(frame_list)
    frames_default = sum(1 for f in frame_list if f["is_default_title"])
    frames_renamed = frames_total - frames_default
    children_total = sum(len(f["children"]) for f in frame_list)

    return {
        "board_id": board_id,
        "board_name": board_name,
        "board_url": board_url,
        "service_account_id": service_account_id,
        "frames": frame_list,
        "author_frame_counts": author_frame_counts,
        "modifier_frame_counts": modifier_frame_counts,
        "members": members,
        "summary": {
            "frames_total": frames_total,
            "frames_renamed": frames_renamed,
            "frames_default": frames_default,
            "children_total": children_total,
        },
    }


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("board_id")
    parser.add_argument("--out")
    args = parser.parse_args()

    result = leer(args.board_id)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        s = result["summary"]
        print(f"BOARD {result['board_name']}  {result['board_url']}")
        print(f"frames: {s['frames_total']} (renombrados {s['frames_renamed']} · "
              f"default {s['frames_default']}) · hijos: {s['children_total']}")
        print(f"service_account: {result['service_account_id']}")
        print(f"-> {args.out}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main()
