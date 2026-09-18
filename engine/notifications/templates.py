"""
CareerOS Executive Candidate Notification Templates
===================================================
Renders high-trust, non-spammy candidate invitation alerts
for Double Opt-In requisition matches.
"""

from typing import Dict, Any

class NotificationTemplateManager:
    """Formats transactional notification copy."""

    @classmethod
    def render_email_html(cls, candidate_alias: str, match_data: Dict[str, Any], consent_url: str) -> str:
        job_title = match_data.get("job_title", "Executive Leadership Mandate")
        score = Math_round = round(match_data.get("overall_match_score", 88.0))
        comp = match_data.get("target_compensation", {})
        comp_str = comp.get("freelance_tjm") or comp.get("permanent_salary") or comp.get("monthly_retainer") or "Executive Compensation"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>CareerOS Inbound Mandate Match</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 24px; color: #ffffff;">
                    <span style="font-size: 11px; font-family: monospace; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em; color: #818cf8;">CareerOS Double Opt-In Protocol</span>
                    <h2 style="margin: 6px 0 0 0; font-size: 20px; font-weight: 700; color: #ffffff;">New Executive Mandate Match: {score}% Fit</h2>
                </div>
                
                <div style="padding: 24px;">
                    <p style="font-size: 14px; line-height: 1.6; color: #334155; margin-top: 0;">
                        Hello <strong>{candidate_alias}</strong>,
                    </p>
                    <p style="font-size: 14px; line-height: 1.6; color: #334155;">
                        An enterprise recruiter has reviewed your anonymized benchmark and requested an executive introduction for the following mandate:
                    </p>
                    
                    <div style="background: #f1f5f9; border-radius: 8px; border: 1px solid #cbd5e1; padding: 16px; margin: 20px 0;">
                        <div style="font-size: 16px; font-weight: bold; color: #0f172a;">{job_title}</div>
                        <div style="font-size: 13px; color: #475569; margin-top: 4px;">Target Compensation Floor: <strong>{comp_str}</strong></div>
                        <div style="font-size: 13px; color: #059669; font-weight: 600; margin-top: 4px;">Audit Match Score: {score}%</div>
                    </div>
                    
                    <div style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 12px; font-size: 12px; color: #065f46; margin-bottom: 24px;">
                        <strong>🛡️ Privacy Protection:</strong> Your full identity, email, phone number, and detailed resume remain cryptographically locked. The recruiter will only receive your contact information if you accept below.
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{consent_url}&decision=APPROVE" style="display: inline-block; background-color: #4f46e5; color: #ffffff; font-weight: 600; font-size: 14px; padding: 12px 28px; text-decoration: none; border-radius: 8px; box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);">
                            ✓ Accept Introduction & Unlock Dossier
                        </a>
                        <div style="margin-top: 12px;">
                            <a href="{consent_url}&decision=DECLINE" style="font-size: 12px; color: #94a3b8; text-decoration: underline;">
                                Decline (Keep Profile Strictly Locked)
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    @classmethod
    def render_sms_text(cls, candidate_alias: str, job_title: str, score: float, consent_url: str) -> str:
        return (
            f"CareerOS: An enterprise matched your profile ({score:.0f}%) for '{job_title}'. "
            f"Review mandate & grant/decline consent here: {consent_url}"
        )
