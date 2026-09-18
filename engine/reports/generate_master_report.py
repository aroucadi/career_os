import json
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent

def generate_markdown_report(out_file=None):
    cache_dir = _ROOT_DIR / 'cache' / 'gap_analysis'
    synthesis_file = cache_dir / '_synthesis.json'
    
    if not synthesis_file.exists():
        print(f'Synthesis file not found at {synthesis_file}.')
        return None

    synthesis = json.loads(synthesis_file.read_text(encoding='utf-8'))
    
    files = sorted(list(cache_dir.glob('*.json')))
    files = [f for f in files if f.name != '_synthesis.json']

    analyses = []
    for f in files:
        analyses.append(json.loads(f.read_text(encoding='utf-8')))

    md = []
    md.append('# 📊 Comprehensive CV v4 Strategic Gap & Enrichment Audit Report')
    md.append('**Candidate:** Alaa Eddine Roucadi  ')
    md.append('**Target Roles Evaluated:** ' + str(len(analyses)) + ' Job Descriptions  ')
    md.append('**Evaluation Engine:** AI-Powered Multi-Rubric Scorer (Gemini 3.6 Flash)  ')
    md.append('\n---\n')

    md.append('## 1. Executive Summary & Market Fit Overview')
    md.append(synthesis.get('overall_market_fit', ''))
    md.append('\n- **Average Fit Score:** ' + str(round(synthesis.get('average_fit_score', 0), 1)) + ' / 100')
    
    strong = [a for a in analyses if a.get('fit_score', 0) >= 70]
    mod = [a for a in analyses if 50 <= a.get('fit_score', 0) < 70]
    low = [a for a in analyses if a.get('fit_score', 0) < 50]

    md.append('- **Strong Match Roles (≥70):** ' + str(len(strong)))
    md.append('- **Moderate Match Roles (50-69):** ' + str(len(mod)))
    md.append('- **Low Match / High-Gap Roles (<50):** ' + str(len(low)))
    md.append('\n---\n')

    md.append('## 2. Complete Job Description Match Score Matrix')
    md.append('| # | Job Title / Employer | Fit Score | Match Level | Top Strength | Primary Gap |')
    md.append('|---|----------------------|-----------|-------------|--------------|-------------|')
    
    for i, a in enumerate(sorted(analyses, key=lambda x: x.get('fit_score', 0), reverse=True), 1):
        title = a.get('jd_title', a.get('jd_file', ''))
        score = a.get('fit_score', 0)
        label = a.get('fit_label', '')
        
        strengths = a.get('matching_strengths', [])
        top_str = strengths[0][:80] + '...' if strengths else 'N/A'
        
        gaps = a.get('gaps', [])
        top_gap = gaps[0].get('gap', 'N/A') if gaps else 'N/A'
        if isinstance(top_gap, dict): top_gap = top_gap.get('gap', 'N/A')
        
        md.append(f'| {i} | **{title}** | {score}/100 | {label} | {top_str} | {top_gap} |')

    md.append('\n---\n')

    md.append('## 3. High-Frequency ATS Keyword Gap Analysis')
    md.append('Below are the top missing ATS keywords across all evaluated job descriptions: \n')
    
    skill_map = synthesis.get('skill_frequency_map', {})
    sorted_skills = sorted(skill_map.items(), key=lambda x: x[1], reverse=True)
    
    md.append('| Required Skill / Keyword | Frequency Across JDs | Action Required |')
    md.append('|--------------------------|----------------------|-----------------|')
    for skill, freq in sorted_skills[:25]:
        md.append(f'| **{skill}** | {freq} JDs | Add keyword & evidence to CV |')

    md.append('\n---\n')

    md.append('## 4. Priority Gap Closure & Enrichment Roadmap')
    md.append('To close remaining gaps and maximize match scores across all targets, complete the following action plan:\n')
    
    crit_gaps = synthesis.get('critical_gaps_cross_jd', [])
    md.append('| Priority | Skill Gap | Target JDs | Recommended Course / Certification | Personal Project Idea | Timeline | Effort |')
    md.append('|----------|-----------|------------|------------------------------------|-----------------------|----------|--------|')
    for cg in crit_gaps:
        prio = cg.get('priority', 'High')
        gap_name = cg.get('gap', '')
        freq = cg.get('frequency', 1)
        ap = cg.get('action_plan', {})
        course = ap.get('course_or_cert', 'N/A')
        proj = ap.get('personal_project', 'N/A')
        timeframe = ap.get('timeline', '4 weeks')
        effort = ap.get('effort', 'Medium')
        md.append(f'| **{prio}** | {gap_name} | {freq} JDs | {course} | {proj} | {timeframe} | {effort} |')

    md.append('\n---\n')

    md.append('## 5. Section-by-Section CV v4 Bullet Refinement Recommendations')
    md.append('### A. Professional Summary')
    md.append(synthesis.get('positioning_advice', ''))
    
    md.append('\n### B. Consolidated Quick CV Wins (Immediate Rewriting Tips)')
    wins = synthesis.get('quick_wins_consolidated', [])
    for w in wins:
        md.append(f'- ⚡ {w}')

    md.append('\n### C. Target Role Family Alignment')
    rf_list = synthesis.get('recommended_role_families', [])
    for rf in rf_list:
        md.append(f'#### 🎯 {rf.get("role_family", "")}')
        md.append(rf.get("fit_rationale", ""))
        targets = ", ".join(rf.get("top_jds_to_target", []))
        if targets:
            md.append(f'*Best Matching JDs:* {targets}')
        md.append('')

    report_content = '\n'.join(md)
    if out_file is None:
        out_file = _ROOT_DIR / 'CV_Strategic_Gap_Analysis_Report.md'
    else:
        out_file = Path(out_file)
    out_file.write_text(report_content, encoding='utf-8')
    print(f'✅ Master Markdown Report generated: {out_file.absolute()}')
    return out_file

if __name__ == '__main__':
    generate_markdown_report()
