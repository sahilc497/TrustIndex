"""
Build the controlled validation dataset for TRUST Index detector evaluation.
Reuses existing items from data/eval_dataset.json and data/held_out_eval_dataset.json,
and curates structured cases for underrepresented categories (Case Types 2, 3, 4, 5).
"""

import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_PATH = os.path.join(PROJECT_ROOT, "data", "eval_dataset.json")
HELDOUT_PATH = os.path.join(PROJECT_ROOT, "data", "held_out_eval_dataset.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "trust_validation_dataset.json")

with open(EVAL_PATH, "r", encoding="utf-8") as f:
    eval_data = json.load(f)

with open(HELDOUT_PATH, "r", encoding="utf-8") as f:
    heldout_data = json.load(f)

cases = []

# ==========================================
# CASE TYPE 1: Correct + Supported (30 cases)
# ==========================================
# 8 Leave, 8 Reimbursement, 8 WFH, 6 IT Security
leave_items = [x for x in eval_data if x["id"].startswith("leave_")][:8]
reimb_items = [x for x in eval_data if x["id"].startswith("reimb_")][:8]
wfh_items = [x for x in eval_data if x["id"].startswith("wfh_")][:8]
it_items = heldout_data[:6]

for item in leave_items + reimb_items + wfh_items:
    cases.append({
        "id": f"val_c1_{item['id']}",
        "case_type": "Case Type 1: Correct + Supported",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["correct_answer"],
        "expected_status": "Trusted",
        "expected_binary_label": "Supported",
        "error_type": "none",
        "ground_truth_rationale": "The answer directly conveys factual information explicitly documented in the provided source passage."
    })

for item in it_items:
    cases.append({
        "id": f"val_c1_{item['id']}",
        "case_type": "Case Type 1: Correct + Supported",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["correct_answer"],
        "expected_status": "Trusted",
        "expected_binary_label": "Supported",
        "error_type": "none",
        "ground_truth_rationale": "The answer accurately states corporate IT security policy according to the provided source passage."
    })

# ==========================================
# CASE TYPE 2: Incorrect + Unsupported (14 cases)
# ==========================================
unsupported_from_eval = [x for x in eval_data if x["error_type"] == "unsupported_addition"]
for item in unsupported_from_eval:
    cases.append({
        "id": f"val_c2_{item['id']}",
        "case_type": "Case Type 2: Incorrect + Unsupported",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["hallucinated_answer"],
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "unsupported_addition",
        "ground_truth_rationale": f"The answer introduces an ungrounded addition not documented in the evidence ({item['error_explanation']})."
    })

# 3 curated additions:
cases.extend([
    {
        "id": "val_c2_extra_01",
        "case_type": "Case Type 2: Incorrect + Unsupported",
        "query": "What equipment does the company provide for permanent remote employees?",
        "source_doc": "hr_policy_wfh.txt",
        "evidence": "The company provides a laptop and a one-time home office setup allowance of 15,000 INR for employees approved for permanent remote work.",
        "answer": "The company provides a laptop, a one-time setup allowance of 15,000 INR, and a complimentary ergonomic standing desk shipped directly to the employee.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "unsupported_addition",
        "ground_truth_rationale": "The provision of an ergonomic standing desk is ungrounded and unmentioned in the evidence passage."
    },
    {
        "id": "val_c2_extra_02",
        "case_type": "Case Type 2: Incorrect + Unsupported",
        "query": "Which travel expenses are eligible for business reimbursement?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Employees traveling for official business are reimbursed for economy class airfare, train fare, and pre-approved local transport.",
        "answer": "Employees traveling on official business are reimbursed for economy class airfare, train fare, pre-approved local transport, and weekend sightseeing passes.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "unsupported_addition",
        "ground_truth_rationale": "Weekend sightseeing passes are extraneous and completely ungrounded in policy documentation."
    },
    {
        "id": "val_c2_extra_03",
        "case_type": "Case Type 2: Incorrect + Unsupported",
        "query": "How many annual paid leaves do employees get?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Employees are entitled to 20 annual paid leaves per calendar year.",
        "answer": "Employees are entitled to 20 annual paid leaves per calendar year and can take spontaneous rejuvenation days without prior notification.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "unsupported_addition",
        "ground_truth_rationale": "Spontaneous rejuvenation days without notice are not mentioned anywhere in the leave policy."
    }
])

# ==========================================
# CASE TYPE 3: Contradictory (12 cases)
# ==========================================
causal_from_eval = [x for x in eval_data if x["error_type"] == "causal_distortion"]
for item in causal_from_eval:
    cases.append({
        "id": f"val_c3_{item['id']}",
        "case_type": "Case Type 3: Contradictory",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["hallucinated_answer"],
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "causal_distortion",
        "ground_truth_rationale": f"The answer asserts a causal justification that directly contradicts the stated policy logic ({item['error_explanation']})."
    })

cases.extend([
    {
        "id": "val_c3_direct_01",
        "case_type": "Case Type 3: Contradictory",
        "query": "Are employees still on probation permitted to work from home?",
        "source_doc": "hr_policy_wfh.txt",
        "evidence": "Employees still on probation are not eligible for work from home under any circumstances.",
        "answer": "Employees still on probation are permitted to work from home with manager approval.",
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "direct_contradiction",
        "ground_truth_rationale": "The answer directly contradicts the explicit policy statement that probationers are not eligible under any circumstances."
    },
    {
        "id": "val_c3_direct_02",
        "case_type": "Case Type 3: Contradictory",
        "query": "Is alcohol ever eligible for business travel reimbursement?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Alcohol is not reimbursable under any circumstances.",
        "answer": "Alcohol is reimbursable if consumed during official client dinners.",
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "direct_contradiction",
        "ground_truth_rationale": "The claim directly contradicts the policy rule that alcohol is not reimbursable under any circumstances."
    },
    {
        "id": "val_c3_direct_03",
        "case_type": "Case Type 3: Contradictory",
        "query": "Can unused sick leave days be carried forward into the following year?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Sick leave cannot be carried forward and unused sick leave is not paid out upon resignation.",
        "answer": "Unused sick leave can be carried forward into the next year.",
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "direct_contradiction",
        "ground_truth_rationale": "The claim asserts that sick leave can be carried forward, directly contradicting the text."
    },
    {
        "id": "val_c3_direct_04",
        "case_type": "Case Type 3: Contradictory",
        "query": "Can reimbursement claims submitted after 30 days be processed without executive sign-off?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Claims submitted after 30 days will not be processed except with written approval from the finance director.",
        "answer": "Claims submitted after 30 days will be processed automatically without requiring executive approval.",
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "direct_contradiction",
        "ground_truth_rationale": "The answer asserts automatic processing without approval, directly contradicting the requirement for finance director sign-off."
    },
    {
        "id": "val_c3_direct_05",
        "case_type": "Case Type 3: Contradictory",
        "query": "Is multi-factor authentication mandatory for all corporate systems?",
        "source_doc": "it_security_policy.txt",
        "evidence": "All corporate systems require multi-factor authentication managed through Okta.",
        "answer": "Multi-factor authentication is optional for standard corporate systems.",
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "direct_contradiction",
        "ground_truth_rationale": "The claim asserts MFA is optional, directly contradicting that all systems require MFA."
    },
    {
        "id": "val_c3_direct_06",
        "case_type": "Case Type 3: Contradictory",
        "query": "Can access credentials ever be shared over Slack?",
        "source_doc": "it_security_policy.txt",
        "evidence": "Access credentials must never be shared over Slack or external messaging tools.",
        "answer": "Access credentials can be shared over Slack if encrypted with a password.",
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "direct_contradiction",
        "ground_truth_rationale": "The claim permits sharing credentials over Slack, directly violating the prohibition that they must never be shared."
    }
])

# ==========================================
# CASE TYPE 4: Partially Supported (12 cases)
# ==========================================
cases.extend([
    {
        "id": "val_c4_part_01",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What are the annual leave allowances and sabbatical terms?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Employees are entitled to 20 annual paid leaves per calendar year. Unused annual leave can be carried forward to the next year for a maximum of 1 year.",
        "answer": "Employees are entitled to 20 annual paid leaves per calendar year, and employees can take unlimited sabbaticals.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "The first claim (20 annual leaves) is fully supported by the evidence, but the second claim (unlimited sabbaticals) is ungrounded."
    },
    {
        "id": "val_c4_part_02",
        "case_type": "Case Type 4: Partially Supported",
        "query": "Can annual leave be carried forward and converted to equity?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Unused annual leave can be carried forward to the next year for a maximum of 1 year.",
        "answer": "Unused annual leave can be carried forward for a maximum of 1 year, and carried forward leave can be converted into company equity.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "The 1-year carry forward is supported, but conversion to equity is completely ungrounded."
    },
    {
        "id": "val_c4_part_03",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What is the sick leave policy and wellness donation program?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Employees receive 10 paid sick leaves per calendar year. Sick leave exceeding 3 consecutive days requires a medical certificate.",
        "answer": "Employees receive 10 paid sick leaves per calendar year, and unused sick leaves are donated to a team wellness fund.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "Receiving 10 sick leaves is supported, while donation to a wellness fund is ungrounded."
    },
    {
        "id": "val_c4_part_04",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What are the maternity leave benefits and childcare provisions?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Female employees are entitled to 26 weeks of paid maternity leave. Maternity leave must be applied for at least 8 weeks before the expected delivery date.",
        "answer": "Female employees are entitled to 26 weeks of paid maternity leave, and the company provides on-site infant daycare facilities.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "The 26 weeks of paid maternity leave is supported, but on-site infant daycare is ungrounded."
    },
    {
        "id": "val_c4_part_05",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What are the leave rules during the 90-day probation period?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Employees on probation (first 90 days of employment) are entitled to 5 paid leaves only. Full leave entitlements apply once probation is successfully completed.",
        "answer": "Employees on probation are entitled to 5 paid leaves only, and probationers are granted weekly study leave afternoons.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "The 5 paid leaves entitlement is supported, but weekly study leave afternoons are ungrounded."
    },
    {
        "id": "val_c4_part_06",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What is the travel booking policy and weekend accommodation allowance?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Employees traveling for official business are reimbursed for economy class airfare, train fare, and pre-approved local transport.",
        "answer": "Employees traveling for official business are reimbursed for economy class airfare, and luxury spa resort fees are reimbursable on weekends.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "Economy class airfare is supported, while luxury spa resort reimbursement is ungrounded."
    },
    {
        "id": "val_c4_part_07",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What is the daily meal allowance for travel within India and abroad?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Employees on official travel receive a daily meal allowance of 1,200 INR within India and 40 USD for international travel.",
        "answer": "Employees receive a daily meal allowance of 1,200 INR within India, and international meal stipends include an open bar tab.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "The 1,200 INR meal allowance is supported, but an open bar tab is ungrounded."
    },
    {
        "id": "val_c4_part_08",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What is the remote internet stipend and streaming subscription allowance?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Employees approved for permanent remote work receive a monthly internet reimbursement of 1,000 INR. This reimbursement is not available to employees on the standard hybrid work arrangement.",
        "answer": "Permanent remote employees receive a monthly internet reimbursement of 1,000 INR, and employees are reimbursed for entertainment streaming subscriptions.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "The 1,000 INR internet reimbursement is supported, but entertainment streaming subscriptions are ungrounded."
    },
    {
        "id": "val_c4_part_09",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What are the approval thresholds for expense claims?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "All reimbursement claims above 5,000 INR require approval from both the reporting manager and the finance department. Claims below 5,000 INR require only reporting manager approval.",
        "answer": "Claims below 5,000 INR require only reporting manager approval, and claims above 100,000 INR require approval from the Board of Directors.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "Manager approval for claims under 5,000 INR is supported, but Board of Directors approval is ungrounded."
    },
    {
        "id": "val_c4_part_10",
        "case_type": "Case Type 4: Partially Supported",
        "query": "Who is eligible to work from home and what are the home gym subsidies?",
        "source_doc": "hr_policy_wfh.txt",
        "evidence": "Employees who have completed 6 months of continuous employment are eligible to apply for work-from-home arrangements.",
        "answer": "Employees who have completed 6 months of continuous employment are eligible to apply for work from home, and the company reimburses commercial gym memberships.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "The 6-month eligibility is supported, while commercial gym membership reimbursement is ungrounded."
    },
    {
        "id": "val_c4_part_11",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What equipment and transportation passes are provided for remote employees?",
        "source_doc": "hr_policy_wfh.txt",
        "evidence": "The company provides a laptop and a one-time home office setup allowance of 15,000 INR for employees approved for permanent remote work.",
        "answer": "The company provides a laptop for employees approved for permanent remote work, and remote employees receive electric bicycle vouchers.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "Laptop provision is supported, while electric bicycle vouchers are ungrounded."
    },
    {
        "id": "val_c4_part_12",
        "case_type": "Case Type 4: Partially Supported",
        "query": "What authentication platform and hardware tokens are required by IT security?",
        "source_doc": "it_security_policy.txt",
        "evidence": "All corporate systems require multi-factor authentication managed through Okta. Employees handling sensitive source code are issued a YubiKey hardware security key.",
        "answer": "Multi-factor authentication is managed through Okta, and biometric eye scanners are deployed to all employee home workstations.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "partially_supported",
        "ground_truth_rationale": "Okta MFA is supported, while biometric eye scanners are ungrounded."
    }
])

# ==========================================
# CASE TYPE 5: Irrelevant Evidence (10 cases)
# ==========================================
cases.extend([
    {
        "id": "val_c5_irrel_01",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "Are employees paid out for unused annual leave when resigning?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Sick leave exceeding 3 consecutive days requires a medical certificate submitted to HR within 5 working days of returning to work.",
        "answer": "Employees who resign are paid out for unused annual leave at their final gross salary rate.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage covers sick leave medical certificates, providing no evidence about resignation payout."
    },
    {
        "id": "val_c5_irrel_02",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "How many days advance notice is required to request annual leave?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Employees on probation (first 90 days of employment) are entitled to 5 paid leaves only.",
        "answer": "Annual leave must be requested at least 3 working days in advance through the HR portal.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage discusses probation leave allowances, providing no evidence regarding advance notice rules."
    },
    {
        "id": "val_c5_irrel_03",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "How many weeks of paternity leave do male employees receive?",
        "source_doc": "hr_policy_leave.txt",
        "evidence": "Unused annual leave can be carried forward to the next year for a maximum of 1 year.",
        "answer": "Male employees are entitled to 2 weeks of paid paternity leave.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage covers annual leave carryover, not paternity leave."
    },
    {
        "id": "val_c5_irrel_04",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "What is the daily meal allowance for business travel within India?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "All reimbursement claims above 5,000 INR require approval from both the reporting manager and the finance department.",
        "answer": "Employees on official travel receive a daily meal allowance of 1,200 INR within India.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage specifies approval workflows for 5,000 INR claims, providing no information regarding meal allowances."
    },
    {
        "id": "val_c5_irrel_05",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "Can remote employees claim monthly phone bill reimbursements?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Employees traveling for official business are reimbursed for economy class airfare, train fare, and pre-approved local transport.",
        "answer": "Phone bill reimbursement of up to 500 INR per month is available to employees in sales and client-facing roles only.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage covers travel transport fares, offering no evidence about phone bill policies."
    },
    {
        "id": "val_c5_irrel_06",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "Within how many days must reimbursement claims be submitted?",
        "source_doc": "hr_policy_reimbursement.txt",
        "evidence": "Employees approved for permanent remote work receive a monthly internet reimbursement of 1,000 INR.",
        "answer": "Reimbursement claims must be submitted within 30 days of the expense being incurred.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage covers remote internet reimbursement, providing no evidence about claim submission deadlines."
    },
    {
        "id": "val_c5_irrel_07",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "What are the mandatory core working hours for remote employees?",
        "source_doc": "hr_policy_wfh.txt",
        "evidence": "The company provides a laptop and a one-time home office setup allowance of 15,000 INR for employees approved for permanent remote work.",
        "answer": "All employees must be available online between 10:00 AM and 4:00 PM IST.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage describes hardware allowances, providing no information regarding working hours."
    },
    {
        "id": "val_c5_irrel_08",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "How many days per week can customer-facing employees work from home?",
        "source_doc": "hr_policy_wfh.txt",
        "evidence": "Approval is granted by the direct reporting manager and must be renewed every 6 months.",
        "answer": "Employees in customer-facing roles may work from home up to 1 day per week only.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage explains 6-month renewal approvals, not weekly frequency caps."
    },
    {
        "id": "val_c5_irrel_09",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "Who must approve privileged access requests in writing?",
        "source_doc": "it_security_policy.txt",
        "evidence": "Corporate production workloads may only be deployed to Amazon Web Services (AWS).",
        "answer": "Requests for privileged access must be approved in writing by the Chief Information Security Officer (CISO).",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence passage discusses cloud deployment on AWS, providing no evidence regarding privileged access approvals."
    },
    {
        "id": "val_c5_irrel_10",
        "case_type": "Case Type 5: Irrelevant Evidence",
        "query": "Within how many hours must lost or stolen devices be reported?",
        "source_doc": "it_security_policy.txt",
        "evidence": "All corporate systems require multi-factor authentication managed through Okta.",
        "answer": "Lost or stolen devices must be reported to the IT Service Desk within 2 hours.",
        "expected_status": "Uncertain",
        "expected_binary_label": "Unsupported",
        "error_type": "irrelevant_evidence",
        "ground_truth_rationale": "The evidence discusses Okta multi-factor authentication, providing no evidence about device loss reporting timeframes."
    }
])

# ==========================================
# CASE TYPE 6: Negation Error (12 cases)
# ==========================================
negation_items = [x for x in eval_data if x["error_type"] == "negation"]
for item in negation_items:
    cases.append({
        "id": f"val_c6_{item['id']}",
        "case_type": "Case Type 6: Negation Error",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["hallucinated_answer"],
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "negation",
        "ground_truth_rationale": f"The answer inverts policy polarity ({item['error_explanation']})."
    })

# ==========================================
# CASE TYPE 7: Numerical Error (20 cases)
# ==========================================
numeric_items = [x for x in eval_data if x["error_type"] in ("numeric_substitution", "date_change")][:20]
for item in numeric_items:
    cases.append({
        "id": f"val_c7_{item['id']}",
        "case_type": "Case Type 7: Numerical Error",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["hallucinated_answer"],
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "numeric_substitution",
        "ground_truth_rationale": f"The answer contains a numerical or temporal error ({item['error_explanation']})."
    })

# ==========================================
# CASE TYPE 8: Entity Substitution (20 cases)
# ==========================================
# 15 from main benchmark, 5 from held-out benchmark
entity_main = [x for x in eval_data if x["error_type"] == "entity_swap"][:15]
entity_heldout = heldout_data[:5]

for item in entity_main:
    cases.append({
        "id": f"val_c8_{item['id']}",
        "case_type": "Case Type 8: Entity Substitution",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["hallucinated_answer"],
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "entity_swap",
        "ground_truth_rationale": f"The answer substitutes a critical entity/role ({item['error_explanation']})."
    })

for item in entity_heldout:
    cases.append({
        "id": f"val_c8_{item['id']}",
        "case_type": "Case Type 8: Entity Substitution",
        "query": item["query"],
        "source_doc": item["source_doc"],
        "evidence": item["source_passage"],
        "answer": item["hallucinated_answer"],
        "expected_status": "Hallucinated",
        "expected_binary_label": "Unsupported",
        "error_type": "entity_swap",
        "ground_truth_rationale": f"The answer substitutes a novel entity in IT security ({item['error_explanation']})."
    })

# Save the dataset
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(cases, f, indent=2)

print(f"Validation dataset created successfully with {len(cases)} items at: {OUTPUT_PATH}")

# Breakdown report
type_counts = {}
status_counts = {}
binary_counts = {}
for c in cases:
    t = c["case_type"]
    type_counts[t] = type_counts.get(t, 0) + 1
    s = c["expected_status"]
    status_counts[s] = status_counts.get(s, 0) + 1
    b = c["expected_binary_label"]
    binary_counts[b] = binary_counts.get(b, 0) + 1

print("\n--- CASE TYPE DISTRIBUTION ---")
for t in sorted(type_counts.keys()):
    print(f"  {t}: {type_counts[t]}")

print("\n--- EXPECTED STATUS BREAKDOWN ---")
for s, cnt in status_counts.items():
    print(f"  {s}: {cnt}")

print("\n--- EXPECTED BINARY BREAKDOWN ---")
for b, cnt in binary_counts.items():
    print(f"  {b}: {cnt}")
