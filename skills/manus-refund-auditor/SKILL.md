---
name: manus-refund-auditor
description: Fully automated end-to-end skill to audit agent threads for credit waste, identify technical failures (Tool Misuse), generate evidence, draft the claim, and fill out the Manus feedback form. Use when the user asks to audit a thread, calculate wasted credits, or prepare a refund request for Manus support.
---

# Manus Refund Auditor (End-to-End)

This skill provides a fully automated, end-to-end methodology for auditing Manus agent threads, identifying credit waste caused by technical failures, generating evidence, and submitting highly effective refund claims based on the official Manus refund policy.

## Core Philosophy

Manus **only** refunds credits for "technical issues on our end" or "Tool Misuse" (when the agent uses a tool incorrectly in a way that violates instructions). They **do not** refund for generic "inefficiency" or "bad answers". 

Therefore, every audit and claim MUST be framed around a specific technical failure, most commonly **Tool Routing Failure** (e.g., using the visual browser for data extraction when an API or scraper was available and functional).

## End-to-End Automated Workflow

When asked to audit a thread or prepare a refund claim, execute this exact sequence without stopping:

### 1. Audit the Thread (The Diagnosis)
Analyze the entire conversation history to identify the root cause of credit waste.
- Look for repeated use of `browser_navigate`, `browser_scroll`, `browser_click` for tasks that could be solved with APIs, `search`, or `shell` scripts.
- Identify if the agent *knew* how to do it right but reverted to the wrong tool (this proves technical failure).
- Calculate the **Inefficiency Factor**: (Actual Credits Used) / (Estimated Optimal Credits).
- Create `auditoria_desperdicio.md` with the chronological breakdown and violated rules.

### 2. Generate Visual Evidence
Run the provided Python script to generate charts proving the waste.
- Run `python3 /home/ubuntu/skills/manus-refund-auditor/scripts/generate_charts.py <actual_credits> <optimal_credits>`
- This creates `evidencia_creditos.png` and `evidencia_timeline.png`.

### 3. Draft the Formal Claim
Create the exact message for support using the template.
- Read `/home/ubuntu/skills/manus-refund-auditor/templates/claim_template.md`.
- Create `reclamo_final.md` filling in the specific details of the audited thread.
- **Crucial**: Maintain a professional, objective tone. Frame it as a "Tool Misuse" bug report.

### 4. Automate Form Submission (The End-to-End Magic)
Do not just give the files to the user. Open the form and fill it out for them.
1. Use `browser_navigate` to open `https://manus.im/feedback`.
2. Use `browser_click` to select "Task report" in the Issue Type dropdown.
3. Use `browser_console_exec` to inject the content of `reclamo_final.md` into the Issue description textarea (to avoid timeouts).
4. Use `browser_console_exec` to make the hidden file input visible.
5. Use `browser_upload_file` to upload `evidencia_creditos.png` and `evidencia_timeline.png`.
6. Ask the user for their Task Link and Email (if not already known).
7. Use `browser_input` to fill the Shared link and Your email fields.

### 5. Final Confirmation
Once the form is 100% filled and verified via `browser_view`, use the `message` tool with `suggested_action: confirm_browser_operation` to ask the user: "El formulario está 100% listo. ¿Confirmo el envío?".
- When the user confirms, use `browser_click` to hit the Send button.
- Save all generated files to the user's Google Drive as a backup.

## Reference Materials

- **Official Policy**: Read `/home/ubuntu/skills/manus-refund-auditor/references/manus_policy.md` to understand exactly what qualifies for a refund.
- **Submission Guide**: Read `/home/ubuntu/skills/manus-refund-auditor/references/submission_guide.md` for the exact steps the user must take to submit the claim.
