#!/usr/bin/env python3
"""
Generic exercise-board stamper for Miro (course-factory plugin · skill miro-boards).

Capa EJECUTOR (Haiku/Bash): determinista, sin criterio. Recibe un build-spec JSON que autora
Sonnet (capa 3) desde la spec del ejercicio y el patrón que eligió Opus (capas 1–2), y estampa el
board completo vía la REST API v2 de Miro.

Uso:
    export MIRO_TOKEN=...            # token de la app (NO se guarda en el repo)
    python3 estampar.py build  <build-spec.json>
    python3 estampar.py clone  <boardId> "<nuevo nombre>"   # ⚠️ NO USAR — ver abajo

⚠️ `clone` (copy_from) NO es fiable: verificado en S1 (2026-07-05) crea el board pero VACÍO (0 ítems).
   Para clonar plantilla→secciones, re-corre `build` con el mismo build-spec cambiando solo board.name.

build-spec.json (todos los patrones caben: A tabla+sticky · B mapa mental · C capturas):
{
  "board": {"name": "<prefix>-<space>-<ss>-<ee>-<Nombre>", "description": "nombre largo / notas"},
  "team_id": "...",                                      # OBLIGATORIO — course.yaml tool_stack.miro.team_id
  "grid":  {"cols":5,"rows":8,"step_x":1440,"step_y":1580,
            "frame_w":1336,"frame_h":1450,"frame_title":"ID y Nombre"},
  "items": [   # coords de hijos: (x,y)=CENTRO del ítem desde la esquina sup-izq del frame
    {"kind":"shape","alias":"hdr","shape":"rectangle","x":668,"y":240,"w":1336,"h":480,
     "content":"<p>Sector seleccionado</p>","fill":"#F5E63D","text_color":"#1a1a1a",
     "align":"left","valign":"top","font_size":30},
    {"kind":"sticky","x":750,"y":330,"w":200,"fill":"light_yellow","content":""},
    {"kind":"text","x":668,"y":700,"w":1100,"content":"...","font_size":24},
    {"kind":"connector","from":"aliasA","to":"aliasB"}    # une dos ítems del MISMO frame por alias
  ]
}
"""
import os, sys, json, time, urllib.request, urllib.error

TOKEN = os.environ.get("MIRO_TOKEN")
API = "https://api.miro.com"


def _req(method, path, body=None):
    if not TOKEN:
        sys.exit("ERROR: falta la variable de entorno MIRO_TOKEN (alerta al conductor).")
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(1 + attempt)
                continue
            sys.exit(f"ERROR HTTP {e.code} en {method} {path}: {msg}\n(alerta al conductor)")
        except Exception as ex:  # noqa
            if attempt < 4:
                time.sleep(1 + attempt)
                continue
            sys.exit(f"ERROR de red en {method} {path}: {ex}\n(alerta al conductor)")


def _shape(bid, fid, it):
    b = {"data": {"shape": it.get("shape", "rectangle"), "content": it.get("content", "")},
         "position": {"x": it["x"], "y": it["y"]}, "parent": {"id": fid},
         "geometry": {"width": it["w"], "height": it["h"]},
         "style": {"fillColor": it.get("fill", "#ffffff"),
                   "color": it.get("text_color", "#1a1a1a"),
                   "borderColor": it.get("border", it.get("fill", "#1a1a1a")),
                   "borderWidth": it.get("border_width", 2),
                   "fontSize": it.get("font_size", 28),
                   "textAlign": it.get("align", "left"),
                   "textAlignVertical": it.get("valign", "top")}}
    return _req("POST", f"/v2/boards/{bid}/shapes", b)["id"]


def _text(bid, fid, it):
    b = {"data": {"content": it.get("content", "")},
         "position": {"x": it["x"], "y": it["y"]}, "parent": {"id": fid},
         "geometry": {"width": it["w"]},
         "style": {"color": it.get("text_color", "#1a1a1a"),
                   "fontSize": it.get("font_size", 24),
                   "textAlign": it.get("align", "left")}}
    return _req("POST", f"/v2/boards/{bid}/texts", b)["id"]


def _sticky(bid, fid, it):
    b = {"data": {"content": it.get("content", "")},
         "position": {"x": it["x"], "y": it["y"]}, "parent": {"id": fid},
         "geometry": {"width": it.get("w", 200)},
         "style": {"fillColor": it.get("fill", "light_yellow")}}
    return _req("POST", f"/v2/boards/{bid}/sticky_notes", b)["id"]


def _connector(bid, sid, eid):
    _req("POST", f"/v2/boards/{bid}/connectors",
         {"startItem": {"id": sid}, "endItem": {"id": eid}})


def build(spec):
    team_id = spec.get("team_id")
    if not team_id:
        sys.exit("ERROR: build-spec sin team_id — copia course.yaml tool_stack.miro.team_id "
                 "(no hay default; alerta al conductor).")
    board = _req("POST", "/v2/boards", {
        "name": spec["board"]["name"][:60],
        "description": spec["board"].get("description", ""),
        "teamId": team_id})
    bid = board["id"]
    url = board.get("viewLink") or f"https://miro.com/app/board/{bid}"
    print(f"BOARD {bid}  {url}")

    g = spec["grid"]
    items = spec.get("items", [])
    n = 0
    for f in range(g["rows"]):
        for c in range(g["cols"]):
            fr = _req("POST", f"/v2/boards/{bid}/frames", {
                "data": {"title": g.get("frame_title", "ID y Nombre"),
                         "format": "custom", "type": "freeform"},
                "position": {"x": c * g["step_x"], "y": f * g["step_y"]},
                "geometry": {"width": g["frame_w"], "height": g["frame_h"]},
                "style": {"fillColor": g.get("frame_fill", "#ffffff")}})
            fid = fr["id"]
            alias = {}
            for it in items:
                k = it["kind"]
                if k == "connector":
                    continue
                iid = _shape(bid, fid, it) if k == "shape" else \
                      _text(bid, fid, it) if k == "text" else \
                      _sticky(bid, fid, it)
                if it.get("alias"):
                    alias[it["alias"]] = iid
            for it in items:
                if it["kind"] == "connector":
                    _connector(bid, alias[it["from"]], alias[it["to"]])
            n += 1
            print(f"  frame ({c},{f}) {fid}  [{n}/{g['rows']*g['cols']}]")
    print(f"DONE {n} frames  ->  {url}")
    return url


def clone(board_id, new_name):
    b = _req("POST", f"/v2/boards?copy_from={board_id}", {"name": new_name[:60]})
    bid = b["id"]
    url = b.get("viewLink") or f"https://miro.com/app/board/{bid}"
    print(f"CLONE {bid}  {url}")
    return url


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "build":
        with open(sys.argv[2], encoding="utf-8") as fh:
            build(json.load(fh))
    elif len(sys.argv) >= 4 and sys.argv[1] == "clone":
        clone(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
