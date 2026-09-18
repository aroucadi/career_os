"""
cv_gap_analysis.py
==================
Evaluates candidate resume (v6) against target Job Descriptions stored in general_instruction/07_TARGET_JDS/.
Injects general instructions, rubrics, ATS guidelines, recruiter heuristics, bullet transformers, and executive presence scorecards into the LLM evaluation pipeline.
Produces a rich interactive HTML dashboard: cv_gap_report.html

Usage:
    python cv_gap_analysis.py [--cv PATH] [--jd-dir PATH] [--model MODEL] [--out PATH] [--cache]

Defaults:
    --cv     resume/Alaa_Eddine_Roucadi_Resume_v6.md
    --jd-dir general_instruction/07_TARGET_JDS
    --model  gemini-3.6-flash  (override via DEFAULT_MODEL env or --model)
    --out    cv_gap_report.html
    --cache  (flag) cache per-JD results in cache/gap_analysis/
"""

import os, sys, json, argparse, logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)

_ENGINE_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _ENGINE_DIR.parent
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DEFAULT_MODEL, MODEL_PARAMETERS
from llm_utils import initialize_llm_provider, extract_json_from_response
from rubric_loader import get_injected_rubrics_prompt

DEFAULT_CV      = str(_ROOT_DIR / "Alaa_Eddine_Roucadi_Resume_v12.md")
DEFAULT_JD_DIR  = str(_ROOT_DIR / "07_TARGET_JDS")
DEFAULT_OUT     = str(_ROOT_DIR / "cv_gap_report.html")

# ─── Prompts ──────────────────────────────────────────────────────────────────

INJECTED_RUBRICS = get_injected_rubrics_prompt()

GAP_SYS = f"""You are a master talent strategist, executive recruiter, and hiring agent evaluator.
Your mission is to perform a rigorous gap analysis and composite scoring between a candidate CV and a target Job Description.
You MUST apply the following General Instruction Framework & Rubrics strictly:

{INJECTED_RUBRICS}

Return ONLY valid JSON — no markdown code blocks, no conversational preamble."""

GAP_USR = '''=== CANDIDATE CV ===
{cv_text}

=== TARGET JOB DESCRIPTION: {jd_title} ===
{jd_text}

Evaluate the fit according to the General Instruction Framework & Rubrics and return JSON with EXACTLY this structure:
{{
  "jd_title": "{jd_title}",
  "fit_score": <integer 0-100, Composite Score = 0.30*ATS + 0.30*Recruiter + 0.20*Impact + 0.20*Match>,
  "fit_label": "<Poor|Moderate|Good|Strong|Excellent>",
  "composite_breakdown": {{
    "ats_score": {{ "score": <int 0-100>, "evidence": "<string>" }},
    "recruiter_score": {{ "score": <int 0-100>, "evidence": "<string>" }},
    "bullet_impact_score": {{ "score": <int 0-100>, "evidence": "<string>" }},
    "target_match_score": {{ "score": <int 0-100>, "evidence": "<string>" }},
    "executive_score": {{ "score": <int 0-100>, "evidence": "<string>" }}
  }},
  "freelance_contract_fit": {{
    "estimated_daily_rate_eur": "<e.g. €750-€1,100/day>",
    "umbrella_title_alignment": "<e.g. AI Platform Product Manager / AI Operating Model Lead>",
    "csuite_deliverable_match": "<AI Operating Model Architecture | Value Stream Optimization | Strategic Portfolio Telemetry>"
  }},
  "executive_summary": "<2-3 sentence honest summary of overall fit>",
  "matching_strengths": ["<bullet>", ...],
  "competency_gaps": ["<missing core competency in AI, product, agile, tech, or governance>", ...],
  "gaps": [
    {{
      "gap": "<missing skill/experience/keyword>",
      "jd_importance": "<Critical|High|Medium|Low>",
      "how_to_close": "<specific course, cert, project, or portfolio piece>"
    }}, ...
  ],
  "quick_wins": ["<CV reframing suggestion>", ...],
  "keywords_missing": ["<exact JD keyword absent from CV>", ...],
  "keywords_present": ["<JD keyword present in CV>", ...],
  "role_reworking_suggestions": [
    {{
      "target_role": "<Current/past CV role title>",
      "proposed_title": "<Optimized role title aligned with JD>",
      "bullet_transformation": "<Original CV bullet -> Re-architected bullet following Google XYZ formula (Accomplished X, measured by Y, by doing Z)>"
    }}, ...
  ]
}}
Rules:
- fit_score: 70+ = competitive, 85+ = strong candidate
- gaps ranked by jd_importance (Critical first)
- role_reworking_suggestions: offer concrete, high-impact bullet transformations using exact terms from this JD while keeping factual candidate experience.
- Return valid JSON only.'''

SYNTH_SYS = f"""You are a senior executive career strategist and hiring agent director.
Given gap analysis results across target job descriptions, synthesise master strategic insights.
Apply the General Instruction Framework & Rubrics:

{INJECTED_RUBRICS}

Return ONLY valid JSON."""

SYNTH_USR = '''=== CANDIDATE CV SUMMARY ===
{cv_text}

=== PER-JD GAP ANALYSIS RESULTS ===
{analyses_json}

Return JSON with EXACTLY this structure:
{{
  "overall_market_fit": "<2-3 sentence honest overall positioning>",
  "average_fit_score": <float>,
  "average_ats_score": <float>,
  "average_recruiter_score": <float>,
  "average_bullet_impact_score": <float>,
  "average_target_match_score": <float>,
  "average_executive_score": <float>,
  "freelance_market_summary": {{
    "target_daily_rate_range": "<e.g. €800-€1,200/day>",
    "top_umbrella_titles": ["<title>", ...],
    "high_ticket_deliverables": ["<deliverable>", ...]
  }},
  "top_strengths_cross_jd": ["<strength present in 3+ JD matches>", ...],
  "top_competency_gaps_cross_jd": ["<competency gap across multiple JDs>", ...],
  "critical_gaps_cross_jd": [
    {{
      "gap": "<topic>",
      "frequency": <int>,
      "priority": "<Critical|High|Medium>",
      "action_plan": {{
        "course_or_cert": "<specific course/cert with provider>",
        "personal_project": "<concrete project idea>",
        "timeline": "<e.g. 4-6 weeks>",
        "effort": "<Low|Medium|High>"
      }}
    }}, ...
  ],
  "quick_wins_consolidated": ["<top CV rewriting tip>", ...],
  "skill_frequency_map": {{ "<skill>": <count>, ... }},
  "positioning_advice": "<3-5 sentences: how to reposition the CV for maximum ATS and executive callback rate>",
  "role_reworking_master_strategy": "<Detailed guidance on how to rework current/past roles to match the 20 JDs>",
  "recommended_role_families": [
    {{
      "role_family": "<e.g. AI Delivery Lead / Agentic Operating Model Director>",
      "fit_rationale": "<why this fits>",
      "top_jds_to_target": ["<jd_title>", ...]
    }}, ...
  ]
}}
Return valid JSON only.'''


# ─── LLM helper ───────────────────────────────────────────────────────────────

import time

def call_llm_json(provider, model: str, sys_msg: str, usr_msg: str, params: dict, retries: int = 4) -> dict:
    for attempt in range(retries):
        try:
            resp = provider.chat(
                model=model,
                messages=[{"role":"system","content":sys_msg},{"role":"user","content":usr_msg}],
                options={"stream":False,"temperature":params.get("temperature",0.1),"top_p":params.get("top_p",0.9)},
            )
            raw = extract_json_from_response(resp["message"]["content"])
            return json.loads(raw)
        except Exception as e:
            if attempt < retries - 1:
                wait_sec = (attempt + 1) * 6
                logger.warning(f"  [RETRY {attempt+1}/{retries}] Error: {e}. Waiting {wait_sec}s...")
                time.sleep(wait_sec)
            else:
                raise e


def analyse_jd(cv_text, jd_path, provider, model, params):
    jd_text  = jd_path.read_text(encoding="utf-8")
    jd_title = jd_path.stem.replace("_"," ").replace("-"," ").title()
    logger.info(f"  Analysing: {jd_title}")
    result = call_llm_json(
        provider, model, GAP_SYS,
        GAP_USR.format(cv_text=cv_text, jd_text=jd_text, jd_title=jd_title),
        params,
    )
    result["jd_file"] = jd_path.name
    result.setdefault("jd_title", jd_title)
    return result


def synthesise(cv_text, analyses, provider, model, params):
    logger.info("Synthesising cross-JD strategic insights...")
    return call_llm_json(
        provider, model, SYNTH_SYS,
        SYNTH_USR.format(cv_text=cv_text, analyses_json=json.dumps(analyses, indent=2, ensure_ascii=False)),
        params,
    )


# ─── HTML report ──────────────────────────────────────────────────────────────

def _color(score):
    if score >= 80: return "#10b981"
    if score >= 65: return "#f59e0b"
    if score >= 50: return "#f97316"
    return "#ef4444"

def _badge(label, colors_map, default="#6b7280"):
    color = colors_map.get(label, default)
    return f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:99px;font-size:12px;font-weight:600">{label}</span>'

FIT_COLORS = {"Excellent":"#10b981","Strong":"#3b82f6","Good":"#6366f1","Moderate":"#f59e0b","Poor":"#ef4444"}
PRI_COLORS = {"Critical":"#ef4444","High":"#f97316","Medium":"#f59e0b","Low":"#10b981"}

def generate_html(analyses, synthesis, cv_path, model_name):
    jd_labels    = [a.get("jd_title", a.get("jd_file","")) for a in analyses]
    fit_scores   = [a.get("fit_score",0) for a in analyses]
    score_colors = [_color(s) for s in fit_scores]

    skill_freq   = synthesis.get("skill_frequency_map",{})
    sorted_skills = sorted(skill_freq.items(), key=lambda x:x[1], reverse=True)[:20]
    skill_labels = [s[0] for s in sorted_skills]
    skill_counts = [s[1] for s in sorted_skills]

    avg_score    = synthesis.get("average_fit_score", 0)
    avg_color    = _color(int(avg_score))
    
    avg_ats      = synthesis.get("average_ats_score", 0)
    avg_rec      = synthesis.get("average_recruiter_score", 0)
    avg_impact   = synthesis.get("average_bullet_impact_score", 0)
    avg_exec     = synthesis.get("average_executive_score", 0)

    # ── Per-JD cards
    jd_cards = ""
    for i, a in enumerate(analyses):
        score  = a.get("fit_score",0)
        color  = _color(score)
        title  = a.get("jd_title","")
        label  = a.get("fit_label","")
        gaps   = a.get("gaps",[])
        cgaps  = a.get("competency_gaps",[])
        kw_m   = a.get("keywords_missing",[])
        kw_p   = a.get("keywords_present",[])
        rework = a.get("role_reworking_suggestions",[])
        bd     = a.get("composite_breakdown",{})

        ats_s  = bd.get("ats_score",{}).get("score", score)
        rec_s  = bd.get("recruiter_score",{}).get("score", score)
        imp_s  = bd.get("bullet_impact_score",{}).get("score", score)
        match_s= bd.get("target_match_score",{}).get("score", score)
        exec_s = bd.get("executive_score",{}).get("score", score)

        strengths_html = "".join(f"<li>{s}</li>" for s in a.get("matching_strengths",[]))
        cgaps_html     = "".join(f"<li>{cg}</li>" for cg in cgaps)
        wins_html      = "".join(f"<li>{w}</li>" for w in a.get("quick_wins",[]))
        
        gaps_html      = "".join(f"""
            <div class="gap-item">
              <div class="gap-header">{_badge(g.get("jd_importance",""),PRI_COLORS)}<strong>{g.get("gap","")}</strong></div>
              <div class="gap-action">💡 {g.get("how_to_close","")}</div>
            </div>""" for g in gaps)
        
        rework_html    = "".join(f"""
            <div class="rework-item">
              <div class="rework-header">📌 Target: <strong>{r.get("target_role","")}</strong> → <span class="rework-title">{r.get("proposed_title","")}</span></div>
              <div class="rework-bullet">🚀 <em>{r.get("bullet_transformation","")}</em></div>
            </div>""" for r in rework)

        kw_present_html = "".join(f'<span class="kw-chip kw-present">{k}</span>' for k in kw_p)
        kw_missing_html = "".join(f'<span class="kw-chip kw-missing">{k}</span>' for k in kw_m)

        jd_cards += f"""
        <div class="jd-card" data-score="{score}" data-title="{title.lower()}">
          <div class="jd-card-header" onclick="toggleCard('jd-body-{i}',this)">
            <div class="jd-title-row">
              <span class="jd-number">#{i+1}</span>
              <span class="jd-title">{title}</span>
              {_badge(label, FIT_COLORS)}
            </div>
            <div class="jd-score-row">
              <div class="score-bar-wrap"><div class="score-bar" style="width:{score}%;background:{color}"></div></div>
              <span class="score-num" style="color:{color}">{score}/100</span>
              <span class="chevron">▼</span>
            </div>
          </div>
          <div class="jd-card-body" id="jd-body-{i}">
            <p class="summary-text">{a.get("executive_summary","")}</p>
            
            <div class="rubric-pills-row">
              <span class="rubric-pill">🤖 ATS Score: <strong>{ats_s}/100</strong></span>
              <span class="rubric-pill">👁️ Recruiter: <strong>{rec_s}/100</strong></span>
              <span class="rubric-pill">💥 Impact (XYZ): <strong>{imp_s}/100</strong></span>
              <span class="rubric-pill">🎯 JD Match: <strong>{match_s}/100</strong></span>
              <span class="rubric-pill">👑 Executive: <strong>{exec_s}/100</strong></span>
            </div>

            <div class="two-col">
              <div><h4>✅ Matching Strengths</h4><ul class="strength-list">{strengths_html}</ul></div>
              <div><h4>⚠️ Competency Gaps</h4><ul class="cgaps-list">{cgaps_html}</ul></div>
            </div>

            <h4>🔍 Gap Analysis & Closing Actions</h4>
            <div class="gaps-container">{gaps_html}</div>

            <h4>🎭 Role Reworking & Bullet Transformations (Google XYZ)</h4>
            <div class="rework-container">{rework_html}</div>

            <h4>🏷️ Keywords Analysis</h4>
            <div class="kw-row">
              <div><strong>Present in CV:</strong><br>{kw_present_html}</div>
              <div><strong>Missing from CV:</strong><br>{kw_missing_html}</div>
            </div>
          </div>
        </div>"""

    # ── Action plan table rows
    action_rows = ""
    for g in synthesis.get("critical_gaps_cross_jd",[]):
        ap = g.get("action_plan",{})
        action_rows += f"""
        <tr>
          <td>{_badge(g.get("priority",""),PRI_COLORS)}</td>
          <td><strong>{g.get("gap","")}</strong></td>
          <td class="center">{g.get("frequency",0)}</td>
          <td>{ap.get("course_or_cert","-")}</td>
          <td>{ap.get("personal_project","-")}</td>
          <td class="center">{ap.get("timeline","-")}</td>
          <td class="center">{ap.get("effort","-")}</td>
        </tr>"""

    # ── Role family cards
    role_cards = ""
    for rf in synthesis.get("recommended_role_families",[]):
        targets = ", ".join(rf.get("top_jds_to_target",[]))
        role_cards += f"""
        <div class="role-card">
          <div class="role-name">{rf.get("role_family","")}</div>
          <p>{rf.get("fit_rationale","")}</p>
          {"<div class='role-targets'>🎯 Best JDs: " + targets + "</div>" if targets else ""}
        </div>"""

    strengths_cross_html   = "".join(f"<li>{s}</li>" for s in synthesis.get("top_strengths_cross_jd",[]))
    cgaps_cross_html       = "".join(f"<li>{cg}</li>" for cg in synthesis.get("top_competency_gaps_cross_jd",[]))
    quick_wins_html        = "".join(f"<li>{w}</li>" for w in synthesis.get("quick_wins_consolidated",[]))
    master_rework_guidance = synthesis.get("role_reworking_master_strategy","")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CV Gap Analysis & General Instruction Dashboard — Alaa Eddine Roucadi</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#0f1117;--surface:#1a1d27;--surface2:#22263a;--border:#2d3148;--accent:#6366f1;--accent2:#818cf8;--text:#e2e8f0;--text2:#94a3b8;--success:#10b981;--warn:#f59e0b;--danger:#ef4444}}
body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}
.header{{background:linear-gradient(135deg,#1e1b4b 0%,#312e81 50%,#1e1b4b 100%);padding:48px 40px 36px;border-bottom:1px solid var(--border)}}
.header h1{{font-size:2rem;font-weight:800;background:linear-gradient(90deg,#818cf8,#a5b4fc,#c7d2fe);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.header-meta{{margin-top:8px;color:var(--text2);font-size:14px}}
.header-meta span{{margin-right:20px}}
.nav{{display:flex;gap:4px;padding:16px 40px 0;background:var(--surface);border-bottom:1px solid var(--border);overflow-x:auto}}
.nav-tab{{padding:10px 20px;border-radius:8px 8px 0 0;cursor:pointer;font-size:14px;font-weight:500;color:var(--text2);border:1px solid transparent;border-bottom:none;white-space:nowrap;transition:all .15s}}
.nav-tab:hover{{color:var(--text);background:var(--surface2)}}
.nav-tab.active{{color:var(--accent2);background:var(--bg);border-color:var(--border)}}
main{{padding:32px 40px}}
.tab-panel{{display:none}}.tab-panel.active{{display:block}}
.kpi-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:32px}}
.kpi-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center}}
.kpi-value{{font-size:2.2rem;font-weight:800;line-height:1}}
.kpi-label{{font-size:11px;color:var(--text2);margin-top:6px;font-weight:500;text-transform:uppercase;letter-spacing:.05em}}
.charts-row{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:32px}}
@media(max-width:900px){{.charts-row{{grid-template-columns:1fr}}}}
.chart-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px}}
.chart-card h3{{font-size:14px;font-weight:600;margin-bottom:16px;color:var(--text2);text-transform:uppercase;letter-spacing:.04em}}
.chart-card canvas{{max-height:320px}}
.insight-box{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:24px}}
.insight-box h3{{font-size:16px;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px}}
.insight-box p,.insight-box li{{color:var(--text2);line-height:1.7}}
.insight-box ul{{padding-left:20px}}
.insight-box li{{margin-bottom:8px}}
.jd-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;margin-bottom:16px;overflow:hidden;transition:border-color .15s}}
.jd-card:hover{{border-color:var(--accent)}}
.jd-card-header{{padding:18px 24px;cursor:pointer;user-select:none}}
.jd-title-row{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.jd-number{{background:var(--surface2);color:var(--text2);font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px}}
.jd-title{{font-weight:700;font-size:15px;flex:1}}
.jd-score-row{{display:flex;align-items:center;gap:12px}}
.score-bar-wrap{{flex:1;height:6px;background:var(--surface2);border-radius:99px;overflow:hidden}}
.score-bar{{height:100%;border-radius:99px}}
.score-num{{font-weight:700;font-size:14px;min-width:50px;text-align:right}}
.chevron{{color:var(--text2);font-size:12px;transition:transform .2s}}
.chevron.open{{transform:rotate(180deg)}}
.jd-card-body{{display:none;padding:0 24px 24px;border-top:1px solid var(--border)}}
.summary-text{{color:var(--text2);margin:16px 0;font-size:14px;line-height:1.7}}
.rubric-pills-row{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}
.rubric-pill{{background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:4px 10px;font-size:12px;color:var(--text2)}}
.rubric-pill strong{{color:var(--accent2)}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:20px}}
@media(max-width:700px){{.two-col,.kw-row{{grid-template-columns:1fr}}}}
h4{{font-size:12px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.05em;margin:16px 0 10px}}
.strength-list,.cgaps-list,.wins-list{{list-style:none;padding:0}}
.strength-list li,.cgaps-list li,.wins-list li{{font-size:13px;color:var(--text2);padding:6px 0 6px 10px;border-bottom:1px solid var(--border);border-left:3px solid var(--success);margin-bottom:6px}}
.cgaps-list li{{border-left-color:var(--danger)}}
.wins-list li{{border-left-color:var(--accent)}}
.gap-item{{background:var(--surface2);border-radius:8px;padding:12px 16px;margin-bottom:8px}}
.gap-header{{display:flex;align-items:center;gap:10px;margin-bottom:6px}}
.gap-header strong{{font-size:14px}}
.gap-action{{font-size:12px;color:var(--text2)}}
.rework-item{{background:var(--surface2);border-left:3px solid var(--accent2);border-radius:6px;padding:12px 16px;margin-bottom:10px}}
.rework-header{{font-size:13px;color:var(--text);margin-bottom:4px}}
.rework-title{{color:var(--success);font-weight:700}}
.rework-bullet{{font-size:12px;color:var(--text2);line-height:1.5}}
.kw-row{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.kw-row>div>strong{{display:block;font-size:12px;color:var(--text2);text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px}}
.kw-chip{{display:inline-block;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:500;margin:3px 2px}}
.kw-present{{background:rgba(16,185,129,.15);color:#6ee7b7;border:1px solid rgba(16,185,129,.3)}}
.kw-missing{{background:rgba(239,68,68,.12);color:#fca5a5;border:1px solid rgba(239,68,68,.25)}}
.table-wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:var(--surface2);padding:12px 16px;text-align:left;font-size:11px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border)}}
td{{padding:12px 16px;border-bottom:1px solid var(--border);vertical-align:top;color:var(--text2)}}
tr:hover td{{background:var(--surface2)}}
.center{{text-align:center}}
.role-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}
.role-card{{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:20px}}
.role-name{{font-size:16px;font-weight:700;color:var(--accent2);margin-bottom:8px}}
.role-card p{{font-size:13px;color:var(--text2);line-height:1.6}}
.role-targets{{margin-top:10px;font-size:12px;color:var(--text2);font-style:italic}}
.filter-bar{{margin-bottom:20px;display:flex;gap:12px;flex-wrap:wrap}}
.filter-input{{flex:1;min-width:200px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px 16px;color:var(--text);font-size:14px;outline:none}}
.filter-input:focus{{border-color:var(--accent)}}
.filter-select{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px 16px;color:var(--text);font-size:14px;cursor:pointer}}
.footer{{text-align:center;padding:32px;color:var(--text2);font-size:12px;border-top:1px solid var(--border);margin-top:40px}}
</style>
</head>
<body>

<div class="header">
  <h1>🎯 CV Gap Analysis & General Instruction Dashboard</h1>
  <div class="header-meta">
    <span>📄 {cv_path}</span>
    <span>🤖 {model_name}</span>
    <span>📋 {len(analyses)} Target JDs</span>
  </div>
</div>

<nav class="nav">
  <div class="nav-tab active" onclick="switchTab('overview',this)">📊 Overview & Rubrics</div>
  <div class="nav-tab" onclick="switchTab('jd-detail',this)">📋 Per-JD Evaluation</div>
  <div class="nav-tab" onclick="switchTab('reworking',this)">🎭 Role Reworking (v7)</div>
  <div class="nav-tab" onclick="switchTab('action-plan',this)">🚀 Action Plan</div>
  <div class="nav-tab" onclick="switchTab('positioning',this)">🧭 Positioning</div>
</nav>

<main>

<!-- OVERVIEW -->
<div class="tab-panel active" id="tab-overview">
  <div class="kpi-row">
    <div class="kpi-card"><div class="kpi-value" style="color:{avg_color}">{avg_score:.0f}</div><div class="kpi-label">Avg Composite Score</div></div>
    <div class="kpi-card"><div class="kpi-value" style="color:var(--accent2)">{avg_ats:.0f}</div><div class="kpi-label">Avg ATS Score</div></div>
    <div class="kpi-card"><div class="kpi-value" style="color:var(--accent2)">{avg_rec:.0f}</div><div class="kpi-label">Avg Recruiter Score</div></div>
    <div class="kpi-card"><div class="kpi-value" style="color:var(--accent2)">{avg_impact:.0f}</div><div class="kpi-label">Avg Bullet Impact</div></div>
    <div class="kpi-card"><div class="kpi-value" style="color:var(--accent2)">{avg_exec:.0f}</div><div class="kpi-label">Avg Executive Score</div></div>
    <div class="kpi-card"><div class="kpi-value" style="color:var(--success)">{len([s for s in fit_scores if s>=70])}</div><div class="kpi-label">Strong Fits ≥70</div></div>
  </div>
  
  <div class="charts-row">
    <div class="chart-card"><h3>Composite Fit Score by JD</h3><canvas id="scoreChart"></canvas></div>
    <div class="chart-card"><h3>Top Required Skills Across 20 JDs</h3><canvas id="skillChart"></canvas></div>
  </div>
  
  <div class="insight-box"><h3>🌐 Overall Market Fit Analysis</h3><p>{synthesis.get("overall_market_fit","")}</p></div>
  
  <div class="two-col">
    <div class="insight-box"><h3>✅ Key Cross-JD Strengths</h3><ul>{strengths_cross_html}</ul></div>
    <div class="insight-box"><h3>⚠️ Key Cross-JD Competency Gaps</h3><ul>{cgaps_cross_html}</ul></div>
  </div>
</div>

<!-- PER-JD -->
<div class="tab-panel" id="tab-jd-detail">
  <div class="filter-bar">
    <input class="filter-input" type="text" id="jd-search" placeholder="🔍 Search job titles…" oninput="filterJDs()">
    <select class="filter-select" id="jd-filter" onchange="filterJDs()">
      <option value="all">All Scores</option>
      <option value="strong">Strong (≥70)</option>
      <option value="moderate">Moderate (50–69)</option>
      <option value="low">Low (&lt;50)</option>
    </select>
  </div>
  <div id="jd-cards-container">{jd_cards}</div>
</div>

<!-- ROLE REWORKING FOR V7 -->
<div class="tab-panel" id="tab-reworking">
  <div class="insight-box">
    <h3>🎭 Role Reworking & Title Strategy for Resume v7</h3>
    <p style="margin-bottom:16px;">{master_rework_guidance}</p>
    <p>Below is the summary of suggested title reframing and bullet transformations (using Google XYZ formula: Accomplished [X], measured by [Y], by doing [Z]) extracted across all target JDs.</p>
  </div>
</div>

<!-- ACTION PLAN -->
<div class="tab-panel" id="tab-action-plan">
  <div class="insight-box"><h3>⚡ Quick CV Wins (No New Skills Needed)</h3><ul>{quick_wins_html}</ul></div>
  <div class="insight-box" style="margin-bottom:0;border-radius:12px 12px 0 0;border-bottom:none"><h3>📚 Strategic Gap Closure Plan</h3></div>
  <div class="table-wrap" style="background:var(--surface);border:1px solid var(--border);border-radius:0 0 12px 12px;overflow:hidden;margin-bottom:24px">
    <table>
      <thead><tr><th>Priority</th><th>Gap / Skill</th><th class="center">JDs</th><th>Course / Cert</th><th>Personal Project</th><th class="center">Timeline</th><th class="center">Effort</th></tr></thead>
      <tbody>{action_rows}</tbody>
    </table>
  </div>
</div>

<!-- POSITIONING -->
<div class="tab-panel" id="tab-positioning">
  <div class="insight-box"><h3>🎯 CV Repositioning Advice</h3><p>{synthesis.get("positioning_advice","")}</p></div>
  <div class="insight-box"><h3>🗂️ Recommended Role Families</h3><div class="role-grid">{role_cards}</div></div>
</div>

</main>
<div class="footer">Generated by cv_gap_analysis.py with General Instruction Rubrics · {len(analyses)} JDs · {model_name}</div>

<script>
const analyses={json.dumps(analyses)};
function switchTab(id,el){{
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  el.classList.add('active');
}}
function toggleCard(bodyId,header){{
  const body=document.getElementById(bodyId);
  const ch=header.querySelector('.chevron');
  const open=body.style.display==='block';
  body.style.display=open?'none':'block';
  ch.classList.toggle('open',!open);
}}
function filterJDs(){{
  const q=document.getElementById('jd-search').value.toLowerCase();
  const f=document.getElementById('jd-filter').value;
  document.querySelectorAll('.jd-card').forEach(card=>{{
    const t=card.dataset.title||'';
    const s=parseInt(card.dataset.score||0);
    const ms=t.includes(q);
    const mf=f==='all'||(f==='strong'&&s>=70)||(f==='moderate'&&s>=50&&s<70)||(f==='low'&&s<50);
    card.style.display=ms&&mf?'':'none';
  }});
}}
new Chart(document.getElementById('scoreChart'),{{
  type:'bar',
  data:{{labels:{json.dumps(jd_labels)},datasets:[{{label:'Composite Fit Score',data:{json.dumps(fit_scores)},backgroundColor:{json.dumps(score_colors)},borderRadius:6}}]}},
  options:{{indexAxis:'y',plugins:{{legend:{{display:false}}}},scales:{{x:{{min:0,max:100,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#94a3b8'}}}},y:{{ticks:{{color:'#94a3b8',font:{{size:11}}}},grid:{{display:false}}}}}}}}
}});
new Chart(document.getElementById('skillChart'),{{
  type:'bar',
  data:{{labels:{json.dumps(skill_labels)},datasets:[{{label:'Target JDs Requiring',data:{json.dumps(skill_counts)},backgroundColor:'rgba(99,102,241,.7)',borderColor:'rgba(129,140,248,1)',borderWidth:1,borderRadius:4}}]}},
  options:{{indexAxis:'y',plugins:{{legend:{{display:false}}}},scales:{{x:{{grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#94a3b8',stepSize:1}}}},y:{{ticks:{{color:'#94a3b8',font:{{size:11}}}},grid:{{display:false}}}}}}}}
}});
</script>
</body>
</html>"""


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CV gap analysis against multiple JDs using General Instructions.")
    parser.add_argument("--cv",      default=DEFAULT_CV)
    parser.add_argument("--jd-dir",  default=DEFAULT_JD_DIR)
    parser.add_argument("--model",   default=DEFAULT_MODEL)
    parser.add_argument("--out",     default=DEFAULT_OUT)
    parser.add_argument("--cache",   action="store_true")
    args = parser.parse_args()

    cv_path  = Path(args.cv)
    jd_dir   = Path(args.jd_dir)
    out_path = Path(args.out)
    model    = args.model

    if not cv_path.exists():
        print(f"ERROR: CV not found: {cv_path}"); sys.exit(1)
    if not jd_dir.exists():
        print(f"ERROR: JD dir not found: {jd_dir}"); sys.exit(1)

    jd_files = sorted(list(jd_dir.glob("*.md")) + list(jd_dir.glob("*.txt")))
    if not jd_files:
        print(f"ERROR: No .md/.txt JD files in {jd_dir}"); sys.exit(1)

    logger.info(f"CV: {cv_path}  |  {len(jd_files)} JDs  |  model: {model}")
    cv_text = cv_path.read_text(encoding="utf-8")
    params  = MODEL_PARAMETERS.get(model, {"temperature":0.1,"top_p":0.9})
    provider = initialize_llm_provider(model)

    cache_dir = _ROOT_DIR / "cache" / "gap_analysis"
    if args.cache:
        cache_dir.mkdir(parents=True, exist_ok=True)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_one_jd(jd_path):
        cf = (cache_dir / f"{jd_path.stem}.json") if args.cache else None
        if cf and cf.exists():
            logger.info(f"  [CACHE] {jd_path.name}")
            return json.loads(cf.read_text(encoding="utf-8"))
        else:
            result = analyse_jd(cv_text, jd_path, provider, model, params)
            if cf:
                cf.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            return result

    analyses = []
    for jd_path in jd_files:
        try:
            cf = (cache_dir / f"{jd_path.stem}.json") if args.cache else None
            if cf and cf.exists():
                logger.info(f"  [CACHE] {jd_path.name}")
                result = json.loads(cf.read_text(encoding="utf-8"))
            else:
                result = analyse_jd(cv_text, jd_path, provider, model, params)
                if cf:
                    cf.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                time.sleep(2)
            analyses.append(result)
        except Exception as exc:
            logger.error(f"  [ERROR] {jd_path.name}: {exc}")

    # Sort analyses by filename order to maintain consistent output order
    analyses.sort(key=lambda x: x.get("jd_file", ""))

    # Cross-JD synthesis
    synth_cache = (cache_dir / "_synthesis.json") if args.cache else None
    if synth_cache and synth_cache.exists():
        logger.info("[CACHE] synthesis")
        synthesis = json.loads(synth_cache.read_text(encoding="utf-8"))
    else:
        synthesis = synthesise(cv_text, analyses, provider, model, params)
        if synth_cache:
            synth_cache.write_text(json.dumps(synthesis, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate report
    logger.info(f"Writing report → {out_path}")
    html = generate_html(analyses, synthesis, str(cv_path), model)
    out_path.write_text(html, encoding="utf-8")

    avg = synthesis.get("average_fit_score", 0)
    print(f"\n✅  Report: {out_path.absolute()}")
    print(f"    Avg composite fit score : {avg:.1f}/100")
    print(f"    JDs analysed             : {len(analyses)}")
    print(f"    Strong (≥70)             : {sum(1 for a in analyses if a.get('fit_score',0)>=70)}")
    print(f"    Moderate                 : {sum(1 for a in analyses if 50<=a.get('fit_score',0)<70)}")
    print(f"    Low (<50)                : {sum(1 for a in analyses if a.get('fit_score',0)<50)}")

if __name__ == "__main__":
    main()
