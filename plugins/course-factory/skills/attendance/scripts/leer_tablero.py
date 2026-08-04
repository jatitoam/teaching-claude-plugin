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
título del frame a "<carné> - <nombre>" y aportan su trabajo adentro. Por eso el TÍTULO del frame
es la afirmación (claim), y el contenido del alumno es la señal confiable de autoría.

⚠️ EL CONTENIDO DEL ALUMNO LLEGA POR DOS VÍAS — contar solo una marca presentes como ausentes:
  (a) ítems que el alumno CREA (`createdBy` != cuenta de servicio) → `is_student_created`;
  (b) formas SEMBRADAS (zonas de color del andamiaje) dentro de las cuales el alumno ESCRIBE su
      respuesta en vez de crear un sticky nuevo. Ese ítem conserva el `createdBy` del script del
      instructor, así que por (a) es invisible. Se detecta porque su TEXTO difiere del texto de
      fábrica → `is_student_edited`.
La unión de ambas es `is_student_content`, y es la que hay que usar para juzgar `relevant`.

Cómo se obtiene el texto "de fábrica": de los frames del mismo board que NADIE reclamó (los que
conservan el título por defecto). Sus hijos son el andamiaje intacto, así que el conjunto de sus
textos es la línea base exacta. Se compara contra el CONJUNTO de textos, no por índice de
posición: los frames no siempre traen el mismo número de hijos y el índice se desalinea.

⚠️ `modifiedBy` del ítem NO alcanza como señal por sí solo: arrastrar una sticky sembrada (que es
justo lo que pide más de un ejercicio) cambia `modifiedBy` sin aportar una palabra. El portón es
el TEXTO; `modifiedBy` solo sirve para saber QUIÉN escribió lo que ya se demostró que es nuevo.

El título por defecto (sin reclamar) del frame es "Carné y Nombre"; también se tratan como
default/no reclamado las variantes "Carnet y Nombre", "ID y Nombre" e "ID and Name". Además, si
ninguna de esas aparece, se detecta el título de fábrica como el título MÁS REPETIDO del board
(los lienzos sin reclamar siempre son mayoría o casi).

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
      "student_items": 2,                    // ítems con is_student_content (creados + zonas escritas)
      "children": [
        {"item_id": "...", "type": "sticky_note", "content": "WhatsApp",
         "created_by_id": "<id o null>", "created_by_name": "<nombre o null>",
         "modified_by_id": "<id o null>", "modified_by_name": "<nombre o null>",
         "is_student_created": true,        // el alumno CREÓ el ítem
         "is_student_edited": false,        // forma sembrada cuyo texto difiere del de fábrica
         "is_student_content": true}        // (a) o (b) — ESTA es la que se usa para `relevant`
      ]
    }
  ],
  "author_frame_counts": {"<author_id>": <int>},      // frames donde la cuenta aportó contenido de alumno
  "modifier_frame_counts": {"<account_id>": <int>},   // frames que la cuenta modificó por última vez (≠ servicio)
  "members": {"<id>": "<nombre o null>"},
  "baseline": {                                       // trazabilidad de la detección de (b)
    "default_title": "<título de fábrica detectado>",
    "unclaimed_frames": N,                            // frames que dieron la línea base
    "seeded_texts": N,                                // textos distintos de fábrica
    "reliable": true,                                 // false → no hubo con qué comparar (ver aviso)
    "note": "<explicación legible de la línea base o del aviso>"
  },
  "summary": {"frames_total": N, "frames_renamed": N, "frames_default": N, "children_total": N,
              "frames_with_student_content": N, "student_items_created": N,
              "student_items_edited_in_place": N}
}
"""
import os, sys, json, re, html, time, argparse, urllib.request, urllib.error

TOKEN = os.environ.get("MIRO_TOKEN")
API = "https://api.miro.com"

DEFAULT_TITLES = {"Carné y Nombre", "Carnet y Nombre", "ID y Nombre", "ID and Name"}

# Nº mínimo de frames sin reclamar para fiarse de la línea base de textos de fábrica.
MIN_UNCLAIMED_FOR_BASELINE = 2


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
                # is_default_title se completa luego, al conocer el título de fábrica del board
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
                "modified_by_id": modified_by,
                "modified_by_name": members.get(modified_by),
                # se completan luego de conocer service_account_id y la línea base de fábrica
                "is_student_created": None,
                "is_student_edited": None,
                "is_student_content": None,
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
        f["children"] = children_by_parent.get(fid, [])

    # --- título de fábrica: una de las variantes conocidas; si no, el título más repetido ---
    title_counts = {}
    for f in frames.values():
        title_counts[f["title"]] = title_counts.get(f["title"], 0) + 1
    default_title = next((t for t in title_counts if t.strip() in DEFAULT_TITLES), None)
    if default_title is None and title_counts:
        top, n = max(title_counts.items(), key=lambda kv: kv[1])
        default_title = top if n >= MIN_UNCLAIMED_FOR_BASELINE else None
    for f in frames.values():
        f["is_default_title"] = (f["title"] == default_title) or (f["title"].strip() in DEFAULT_TITLES)

    # --- línea base: los textos del andamiaje, tomados de los frames que NADIE reclamó ---
    unclaimed = [f for f in frames.values() if f["is_default_title"]]
    seeded_texts = {k["content"] for f in unclaimed for k in f["children"]}
    baseline_reliable = len(unclaimed) >= MIN_UNCLAIMED_FOR_BASELINE

    for f in frames.values():
        for k in f["children"]:
            cb = k["created_by_id"]
            k["is_student_created"] = cb is not None and cb != service_account_id
            # (b) forma sembrada cuyo texto ya no es el de fábrica → el alumno escribió dentro.
            # Sin línea base fiable no se puede afirmar: se deja en False y se avisa (ver `baseline`).
            k["is_student_edited"] = bool(
                baseline_reliable
                and not k["is_student_created"]
                and k["content"].strip()
                and k["content"] not in seeded_texts
            )
            k["is_student_content"] = k["is_student_created"] or k["is_student_edited"]
        f["student_items"] = sum(1 for k in f["children"] if k["is_student_content"])

    # author_frame_counts: por autor, cantidad de frames DISTINTOS donde creó >=1 ítem de alumno
    author_frame_sets = {}
    for fid, f in frames.items():
        seen_authors_this_frame = set()
        for k in f["children"]:
            if not k["is_student_content"]:
                continue
            # quien CREÓ el ítem, o —si el alumno escribió dentro de una forma sembrada— quien la editó
            cb = k["created_by_id"] if k["is_student_created"] else k["modified_by_id"]
            if cb and cb != service_account_id and cb not in seen_authors_this_frame:
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
        "baseline": {
            "default_title": default_title,
            "unclaimed_frames": len(unclaimed),
            "seeded_texts": len(seeded_texts),
            "reliable": baseline_reliable,
            "note": ("línea base tomada de los frames sin reclamar del mismo board" if baseline_reliable
                     else "SIN línea base fiable: no se puede detectar el contenido escrito DENTRO de "
                          "las formas sembradas; `is_student_edited` queda en false en todo el board"),
        },
        "summary": {
            "frames_total": frames_total,
            "frames_renamed": frames_renamed,
            "frames_default": frames_default,
            "children_total": children_total,
            "frames_with_student_content": sum(1 for f in frame_list if f["student_items"]),
            "student_items_created": sum(1 for f in frame_list for k in f["children"]
                                         if k["is_student_created"]),
            "student_items_edited_in_place": sum(1 for f in frame_list for k in f["children"]
                                                 if k["is_student_edited"]),
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
        s, b = result["summary"], result["baseline"]
        print(f"BOARD {result['board_name']}  {result['board_url']}")
        print(f"frames: {s['frames_total']} (renombrados {s['frames_renamed']} · "
              f"default {s['frames_default']}) · hijos: {s['children_total']}")
        print(f"contenido de alumno: {s['frames_with_student_content']} frames · "
              f"{s['student_items_created']} ítems creados + "
              f"{s['student_items_edited_in_place']} escritos DENTRO de zonas sembradas")
        print(f"línea base: título de fábrica {b['default_title']!r} · "
              f"{b['unclaimed_frames']} frames sin reclamar · {b['seeded_texts']} textos")
        if not b["reliable"]:
            print("⚠️  SIN línea base fiable — no se detecta lo escrito dentro de las zonas "
                  "sembradas. Los marcos podrían parecer vacíos aunque tengan trabajo: NO cierres "
                  "asistencia con este resultado, avisa al conductor.")
        print(f"service_account: {result['service_account_id']}")
        print(f"-> {args.out}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main()
