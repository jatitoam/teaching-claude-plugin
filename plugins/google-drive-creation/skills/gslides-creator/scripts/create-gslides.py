#!/usr/bin/env python3
"""
create-gslides.py — Creates a styled Google Slides presentation from a JSON spec.

Usage:
    python create-gslides.py <json_file> <folder_url_or_id> <presentation_title>

Arguments:
    json_file            Path to the JSON slide spec (see references/gslides-style-spec.md)
    folder_url_or_id     Google Drive folder URL or bare folder ID
    presentation_title   Title for the Google Slides presentation

Prints the Google Slides URL to stdout.
"""
import json
import os
import re
import sys
import uuid

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]
TOKEN_PATH = os.path.expanduser("~/.config/teaching-claude-plugin/token-slides.json")
CREDS_PATH = os.path.expanduser("~/.config/teaching-claude-plugin/credentials.json")

# ── Color palette ─────────────────────────────────────────────────────────────

N        = "1A237E"
P        = "6540A8"
B        = "2563EB"
W        = "FFFFFF"
LB       = "EEF2FF"
D        = "1F2937"
M        = "9CA3AF"
CB       = "13172E"
CT       = "D4D4D8"
AC       = "38BDF8"
GR       = "10B981"
RE       = "EF4444"
GO       = "F59E0B"
TA       = "F5F7FF"
TB       = "C7D2FE"
GR_LIGHT = "D1FAE5"
GO_LIGHT = "FEF3C7"
B_LIGHT  = "DBEAFE"


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as fh:
            fh.write(creds.to_json())
    return creds


def parse_folder_id(value):
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", value)
    return match.group(1) if match else value


# ── Builder ───────────────────────────────────────────────────────────────────

class Builder:
    def __init__(self):
        self.requests = []
        self._slide_notes = []

    def _id(self):
        return "obj_" + uuid.uuid4().hex[:16]

    def _emu(self, inches):
        return int(inches * 914400)

    def _rgb(self, hex_color):
        h = hex_color.lstrip("#")
        return {
            "red": int(h[0:2], 16) / 255,
            "green": int(h[2:4], 16) / 255,
            "blue": int(h[4:6], 16) / 255,
        }

    def _size_pos(self, x, y, w, h):
        return {
            "size": {
                "width": {"magnitude": self._emu(w), "unit": "EMU"},
                "height": {"magnitude": self._emu(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": self._emu(x), "translateY": self._emu(y),
                "unit": "EMU",
            },
        }

    def slide(self):
        sid = self._id()
        self.requests.append({
            "createSlide": {
                "objectId": sid,
                "slideLayoutReference": {"predefinedLayout": "BLANK"},
            }
        })
        return sid

    def bg(self, sid, hex_color):
        self.requests.append({
            "updatePageProperties": {
                "objectId": sid,
                "pageProperties": {
                    "pageBackgroundFill": {
                        "solidFill": {"color": {"rgbColor": self._rgb(hex_color)}}
                    }
                },
                "fields": "pageBackgroundFill",
            }
        })

    def rect(self, sid, x, y, w, h, fill_hex, border_hex=None):
        oid = self._id()
        self.requests.append({
            "createShape": {
                "objectId": oid,
                "shapeType": "RECTANGLE",
                "elementProperties": {"pageObjectId": sid, **self._size_pos(x, y, w, h)},
            }
        })
        props = {
            "shapeBackgroundFill": {
                "solidFill": {"color": {"rgbColor": self._rgb(fill_hex)}}
            }
        }
        fields = "shapeBackgroundFill"
        if border_hex:
            props["outline"] = {
                "outlineFill": {"solidFill": {"color": {"rgbColor": self._rgb(border_hex)}}},
                "weight": {"magnitude": 14400, "unit": "EMU"},
            }
            fields += ",outline"
        else:
            props["outline"] = {"propertyState": "NOT_RENDERED"}
            fields += ",outline"
        self.requests.append({
            "updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": props,
                "fields": fields,
            }
        })
        return oid

    def pill(self, sid, x, y, w, h, fill_hex):
        oid = self._id()
        self.requests.append({
            "createShape": {
                "objectId": oid,
                "shapeType": "ROUND_RECTANGLE",
                "elementProperties": {"pageObjectId": sid, **self._size_pos(x, y, w, h)},
            }
        })
        self.requests.append({
            "updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {"color": {"rgbColor": self._rgb(fill_hex)}}
                    },
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill,outline",
            }
        })
        return oid

    def txt(self, sid, x, y, w, h, text, size, color_hex,
            bold=False, italic=False, font="Calibri",
            align="START", valign="TOP"):
        oid = self._id()
        self.requests.append({
            "createShape": {
                "objectId": oid,
                "shapeType": "TEXT_BOX",
                "elementProperties": {"pageObjectId": sid, **self._size_pos(x, y, w, h)},
            }
        })
        self.requests.append({
            "insertText": {
                "objectId": oid,
                "text": text,
                "insertionIndex": 0,
            }
        })
        self.requests.append({
            "updateTextStyle": {
                "objectId": oid,
                "textRange": {"type": "ALL"},
                "style": {
                    "bold": bold,
                    "italic": italic,
                    "fontSize": {"magnitude": size, "unit": "PT"},
                    "fontFamily": font,
                    "foregroundColor": {
                        "opaqueColor": {"rgbColor": self._rgb(color_hex)}
                    },
                },
                "fields": "bold,italic,fontSize,fontFamily,foregroundColor",
            }
        })
        para_align = {
            "START": "START", "CENTER": "CENTER", "END": "END",
        }.get(align, "START")
        self.requests.append({
            "updateParagraphStyle": {
                "objectId": oid,
                "textRange": {"type": "ALL"},
                "style": {"alignment": para_align},
                "fields": "alignment",
            }
        })
        if valign != "TOP":
            api_valign = "MIDDLE" if valign == "MIDDLE" else "BOTTOM"
            self.requests.append({
                "updateShapeProperties": {
                    "objectId": oid,
                    "shapeProperties": {"contentAlignment": api_valign},
                    "fields": "contentAlignment",
                }
            })
        return oid

    def _txt_on_shape(self, oid, text, size, color_hex,
                      bold=False, font="Calibri", align="CENTER"):
        self.requests.append({
            "insertText": {
                "objectId": oid,
                "text": text,
                "insertionIndex": 0,
            }
        })
        self.requests.append({
            "updateTextStyle": {
                "objectId": oid,
                "textRange": {"type": "ALL"},
                "style": {
                    "bold": bold,
                    "fontSize": {"magnitude": size, "unit": "PT"},
                    "fontFamily": font,
                    "foregroundColor": {
                        "opaqueColor": {"rgbColor": self._rgb(color_hex)}
                    },
                },
                "fields": "bold,fontSize,fontFamily,foregroundColor",
            }
        })
        self.requests.append({
            "updateParagraphStyle": {
                "objectId": oid,
                "textRange": {"type": "ALL"},
                "style": {"alignment": align},
                "fields": "alignment",
            }
        })
        self.requests.append({
            "updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": {"contentAlignment": "MIDDLE"},
                "fields": "contentAlignment",
            }
        })

    def footer(self, sid):
        self.txt(
            sid, 0.2, 5.42, 9.6, 0.2,
            "Optimizaciones y Desempeño  ·  Cloud Deployment Automation  ·  PDDS · FISICC · Universidad Galileo",
            7, M, align="CENTER",
        )

    def nav_bar(self, sid, title, badge=None):
        self.rect(sid, 0, 0, 10, 0.65, N)
        if badge:
            pill_oid = self.pill(sid, 0.3, 0.12, 1.3, 0.4, P)
            self._txt_on_shape(pill_oid, badge, 12, W, bold=True)
            self.txt(sid, 1.78, 0, 7.9, 0.65, title, 14, W, bold=True, valign="MIDDLE")
        else:
            self.txt(sid, 0.35, 0, 9.3, 0.65, title, 14, W, bold=True, valign="MIDDLE")

    # ── Slide type methods ────────────────────────────────────────────────────

    def title_slide(self, session, topic, date, instructor, ta):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, N)
        self.rect(sid, 0, 0, 1.5, 5.625, P)
        self.txt(sid, 1.8, 0.8, 7.8, 0.65, f"Session {session}", 18, M)
        self.txt(sid, 1.8, 1.4, 7.8, 1.5, topic, 30, W, bold=True)
        self.txt(sid, 1.8, 2.95, 7.8, 0.45, date, 14, M)
        self.txt(sid, 1.8, 3.45, 7.8, 0.35, instructor, 12, M)
        self.txt(sid, 1.8, 3.82, 7.8, 0.35, f"TA: {ta}", 12, M)

    def agenda_slide(self, rows):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, LB)
        self.nav_bar(sid, "Tonight's Plan")
        # Header row
        self.rect(sid, 0.3, 0.78, 1.2, 0.42, N)
        self.rect(sid, 1.5, 0.78, 8.2, 0.42, N)
        self.txt(sid, 0.3, 0.78, 1.2, 0.42, "TIME", 11, W, bold=True, align="CENTER", valign="MIDDLE")
        self.txt(sid, 1.5, 0.78, 8.2, 0.42, "BLOCK", 11, W, bold=True, valign="MIDDLE")
        y = 1.2
        for i, row in enumerate(rows):
            rtype = row.get("type", "")
            if rtype == "exercise":
                fill = GR
                text_color = W
            elif rtype == "demo":
                fill = P
                text_color = W
            elif rtype in ("intro", "wrap"):
                fill = B
                text_color = W
            elif i % 2 == 0:
                fill = W
                text_color = D
            else:
                fill = TA
                text_color = D
            self.rect(sid, 0.3, y, 1.2, 0.52, fill)
            self.rect(sid, 1.5, y, 8.2, 0.52, fill)
            self.txt(sid, 0.3, y, 1.2, 0.52, row.get("time", ""), 11, text_color, bold=True, align="CENTER", valign="MIDDLE")
            self.txt(sid, 1.5, y, 8.2, 0.52, row.get("block", ""), 11, text_color, valign="MIDDLE")
            y += 0.52

    def section_divider(self, title, subtitle=None):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, N)
        self.rect(sid, 0, 0, 2.0, 5.625, P)
        self.txt(sid, 2.3, 1.5, 7.4, 1.5, title, 32, W, bold=True)
        if subtitle:
            self.txt(sid, 2.3, 3.1, 7.4, 0.6, subtitle, 16, M)

    def content_slide(self, title, bullets, background="light"):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, LB if background == "light" else W)
        self.nav_bar(sid, title)
        y = 0.85
        for bullet in bullets:
            if isinstance(bullet, dict) and bullet.get("type") == "heading":
                self.txt(sid, 0.45, y, 9.1, 0.4, bullet.get("text", ""), 13, N, bold=True)
                y += 0.48
            else:
                text = bullet if isinstance(bullet, str) else bullet.get("text", "")
                self.txt(sid, 0.45, y, 9.1, 0.45, f"•  {text}", 13, D)
                y += 0.48

    def demo_marker(self, demo_label, title):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, CB)
        pill_oid = self.pill(sid, 2.8, 1.1, 4.4, 0.6, AC)
        self._txt_on_shape(pill_oid, "▶  LIVE DEMO", 17, N, bold=True)
        self.txt(sid, 0.5, 2.0, 9.0, 0.7, demo_label, 22, M, bold=True, align="CENTER")
        self.txt(sid, 0.5, 2.7, 9.0, 1.1, title, 28, W, bold=True, align="CENTER")

    def step_slide(self, demo, step_n, total, title, code, why, verify="", code_full=None):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, W)
        self.nav_bar(sid, f"{demo}  —  {title}", badge=f"{step_n} / {total}")

        # Code block (top ~60% of content area)
        self.rect(sid, 0.2, 0.72, 9.6, 2.70, CB)
        self.txt(sid, 0.45, 0.82, 9.1, 2.55, code, 10.5, CT, font="Courier New")

        # WHY strip (bottom ~40% of content area)
        self.rect(sid, 0, 3.48, 10, 1.94, GO)
        self.txt(sid, 0.5, 3.48, 9.0, 1.94, why, 26, W, bold=True, align="CENTER", valign="MIDDLE")

        # Collect speaker notes (not rendered on slide)
        notes_parts = []
        if verify:
            notes_parts.append(f"VERIFY:\n{verify}")
        if code_full:
            notes_parts.append(f"FULL CODE:\n{code_full}")
        if notes_parts:
            self._slide_notes.append((sid, "\n\n".join(notes_parts)))

    def callout_slide(self, title, label, headline, detail):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, N)
        self.rect(sid, 0, 0, 10, 0.55, P)
        self.txt(sid, 0.35, 0, 9.3, 0.55, title, 14, W, bold=True, valign="MIDDLE")
        pill_w = max(1.8, len(label) * 0.13 + 0.4)
        pill_oid = self.pill(sid, 0.45, 0.72, pill_w, 0.36, P)
        self._txt_on_shape(pill_oid, label, 11, W, bold=True)
        self.txt(sid, 0.45, 1.2, 9.1, 1.6, headline, 24, W, bold=True)
        self.rect(sid, 0.45, 2.9, 9.1, 0.05, P)
        self.rect(sid, 0.45, 3.05, 9.1, 1.85, "131A4A", border_hex=P)
        self.txt(sid, 0.65, 3.18, 8.7, 1.58, detail, 14, CT)

    def exercise_slide(self, n, title, description):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, N)
        self.rect(sid, 0, 0, 3.2, 5.625, P)
        self.rect(sid, 3.2, 0, 6.8, 5.625, N)
        self.txt(sid, 0.2, 0.9, 2.8, 1.4, f"Exercise\n{n}", 36, W, bold=True, align="CENTER")
        self.txt(sid, 0.2, 2.55, 2.8, 1.5, title, 16, TB, align="CENTER")
        self.txt(sid, 3.5, 0.75, 6.0, 4.35, description, 15, W)

    def dark_code_slide(self, title, code, file_label=None):
        sid = self.slide()
        self.footer(sid)
        self.bg(sid, CB)
        self.rect(sid, 0, 0, 10, 0.55, P)
        self.txt(sid, 0.35, 0, 9.3, 0.55, title, 14, W, bold=True, valign="MIDDLE")
        self.rect(sid, 0.3, 0.7, 9.4, 4.3, "0D1021", border_hex="2E3A59")
        if file_label:
            self.rect(sid, 0.3, 0.7, 9.4, 0.32, P)
            self.txt(sid, 0.3, 0.7, 9.4, 0.32, file_label, 9, W, font="Courier New", valign="MIDDLE")
            self.txt(sid, 0.45, 1.07, 9.1, 3.88, code, 10.5, CT, font="Courier New")
        else:
            self.txt(sid, 0.45, 0.85, 9.1, 4.1, code, 10.5, CT, font="Courier New")


# ── dispatcher ────────────────────────────────────────────────────────────────

def process_slide(b, slide_dict):
    stype = slide_dict.get("type")
    if stype == "title_slide":
        b.title_slide(
            slide_dict["session"],
            slide_dict["topic"],
            slide_dict["date"],
            slide_dict.get("instructor", "Tito Alvarez"),
            slide_dict.get("ta", "Abner Pérez"),
        )
    elif stype == "agenda":
        b.agenda_slide(slide_dict.get("rows", []))
    elif stype == "section_divider":
        b.section_divider(slide_dict["title"], slide_dict.get("subtitle"))
    elif stype == "content":
        b.content_slide(slide_dict["title"], slide_dict.get("bullets", []), slide_dict.get("background", "light"))
    elif stype == "demo_marker":
        b.demo_marker(slide_dict["demo"], slide_dict["title"])
    elif stype == "step":
        b.step_slide(
            slide_dict["demo"],
            slide_dict["step"],
            slide_dict["total"],
            slide_dict["title"],
            slide_dict["code"],
            slide_dict["why"],
            slide_dict.get("verify", ""),
            slide_dict.get("code_full"),
        )
    elif stype == "callout":
        b.callout_slide(slide_dict["title"], slide_dict["label"], slide_dict["headline"], slide_dict["detail"])
    elif stype == "exercise":
        b.exercise_slide(slide_dict["n"], slide_dict["title"], slide_dict["description"])
    elif stype == "code":
        b.dark_code_slide(slide_dict["title"], slide_dict["code"], slide_dict.get("file_label"))
    else:
        print(f"Warning: unknown slide type '{stype}', skipping.", file=sys.stderr)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python create-gslides.py <json_file> <folder_url_or_id> <presentation_title>",
            file=sys.stderr,
        )
        sys.exit(1)

    json_file, folder_arg, title = sys.argv[1], sys.argv[2], sys.argv[3]
    folder_id = parse_folder_id(folder_arg)

    with open(json_file) as f:
        spec = json.load(f)

    creds = get_credentials()
    slides_svc = build("slides", "v1", credentials=creds)
    drive_svc = build("drive", "v3", credentials=creds)

    pres = slides_svc.presentations().create(body={"title": title}).execute()
    pres_id = pres["presentationId"]
    default_slide_id = pres["slides"][0]["objectId"]

    b = Builder()
    for slide_dict in spec.get("slides", []):
        process_slide(b, slide_dict)

    if b.requests:
        slides_svc.presentations().batchUpdate(
            presentationId=pres_id,
            body={"requests": b.requests},
        ).execute()

    slides_svc.presentations().batchUpdate(
        presentationId=pres_id,
        body={"requests": [{"deleteObject": {"objectId": default_slide_id}}]},
    ).execute()

    # Phase 2: write speaker notes to step slides
    if b._slide_notes:
        pres_data = slides_svc.presentations().get(presentationId=pres_id).execute()
        slide_to_notes_oid = {}
        for slide in pres_data.get("slides", []):
            slide_oid = slide["objectId"]
            notes_page = slide.get("slideProperties", {}).get("notesPage", {})
            for el in notes_page.get("pageElements", []):
                if el.get("shape", {}).get("placeholder", {}).get("type") == "BODY":
                    slide_to_notes_oid[slide_oid] = el["objectId"]
                    break
        notes_requests = []
        for slide_oid, notes_text in b._slide_notes:
            notes_oid = slide_to_notes_oid.get(slide_oid)
            if notes_oid:
                notes_requests.append({
                    "insertText": {
                        "objectId": notes_oid,
                        "insertionIndex": 0,
                        "text": notes_text,
                    }
                })
        if notes_requests:
            slides_svc.presentations().batchUpdate(
                presentationId=pres_id,
                body={"requests": notes_requests},
            ).execute()

    drive_svc.files().update(
        fileId=pres_id,
        addParents=folder_id,
        removeParents="root",
        fields="id,parents",
    ).execute()

    print(f"https://docs.google.com/presentation/d/{pres_id}/edit")


if __name__ == "__main__":
    main()
