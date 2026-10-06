/**
 * Curated demonstration scenarios and frozen research evaluation data
 * for the TRUST Index Verification Dashboard.
 * 
 * All metrics match results/FINAL_RESULTS_AND_DISCUSSION.md exactly.
 */

export const DEMO_SCENARIOS = [
  {
    id: 'demo_supported',
    title: 'Demo 1: Annual Leave Entitlement',
    badge: 'Supported',
    badgeColor: 'emerald',
    expectedStatus: 'Trusted',
    expectedScore: 100.0,
    query: 'How many annual paid leaves do employees get?',
    generated_answer: 'Employees are entitled to 20 annual paid leaves per calendar year.',
    retrieved_documents: [
      {
        doc: 'hr_policy_leave.txt',
        text: 'Section 1: Annual Leave. Employees are entitled to 20 annual paid leaves per calendar year. Unused annual leave can be carried forward to the next year for a maximum of 1 year. Annual leave must be requested at least 3 working days in advance through the HR portal.'
      },
      {
        doc: 'hr_policy_leave.txt',
        text: 'Section 3: Maternity and Paternity Leave. Female employees are entitled to 26 weeks of paid maternity leave. Male employees are entitled to 2 weeks of paid paternity leave.'
      }
    ],
    verification: {
      query: 'How many annual paid leaves do employees get?',
      answer: 'Employees are entitled to 20 annual paid leaves per calendar year.',
      trust_score: 100.0,
      status: 'Trusted',
      explanation: 'All claims are well supported by retrieved evidence with no contradictions detected. Full entailment consensus achieved.',
      claims: [
        {
          claim: 'Employees are entitled to 20 annual paid leaves per calendar year',
          consensus: 1.0,
          evidence: [
            {
              doc: 'hr_policy_leave.txt',
              text: 'Employees are entitled to 20 annual paid leaves per calendar year. Unused annual leave can be carried forward to the next year for a maximum of 1 year.',
              similarity: 0.985,
              label: 'ENTAILMENT',
              reason: 'NLI model confirmed entailment from evidence (confidence: 0.998).'
            }
          ]
        }
      ]
    }
  },
  {
    id: 'demo_unsupported',
    title: 'Demo 2: Wellness & Equipment Stipend',
    badge: 'Unsupported Addition',
    badgeColor: 'amber',
    expectedStatus: 'Uncertain',
    expectedScore: 50.0,
    query: 'What is the allowance for health expenses and remote equipment?',
    generated_answer: 'Employees may claim up to 5,000 INR per year for health expenses, plus 100,000 INR for remote equipment.',
    retrieved_documents: [
      {
        doc: 'hr_policy_reimb.txt',
        text: 'Section 4: Health and Wellness. Employees may claim up to 5,000 INR per year for health and wellness expenses including gym memberships and medical checkups.'
      },
      {
        doc: 'hr_policy_reimb.txt',
        text: 'Section 3: Equipment. The company provides a laptop and a one-time home office setup allowance of 15,000 INR for employees approved for permanent remote work.'
      }
    ],
    verification: {
      query: 'What is the allowance for health expenses and remote equipment?',
      answer: 'Employees may claim up to 5,000 INR per year for health expenses, plus 100,000 INR for remote equipment.',
      trust_score: 50.0,
      status: 'Uncertain',
      explanation: 'Claim 2 ("plus 100,000 INR for remote equipment") is not sufficiently corroborated by retrieved evidence passages (evidence states 15,000 INR stipend). Weakest-link score bounded at 50.0%.',
      claims: [
        {
          claim: 'Employees may claim up to 5,000 INR per year for health expenses',
          consensus: 1.0,
          evidence: [
            {
              doc: 'hr_policy_reimb.txt',
              text: 'Section 4: Health and Wellness. Employees may claim up to 5,000 INR per year for health and wellness expenses.',
              similarity: 0.942,
              label: 'ENTAILMENT',
              reason: 'NLI model confirmed entailment from evidence (confidence: 0.976).'
            }
          ]
        },
        {
          claim: 'plus 100,000 INR for remote equipment',
          consensus: 0.0,
          evidence: [
            {
              doc: 'hr_policy_reimb.txt',
              text: 'The company provides a laptop and a one-time home office setup allowance of 15,000 INR for employees approved for permanent remote work.',
              similarity: 0.612,
              label: 'NEUTRAL',
              reason: 'Evidence neither entails nor directly confirms 100,000 INR figure (evidence specifies 15,000 INR). Ungrounded claim.'
            }
          ]
        }
      ]
    }
  },
  {
    id: 'demo_contradictory',
    title: 'Demo 3: Alcohol Travel Reimbursement',
    badge: 'Direct Contradiction',
    badgeColor: 'rose',
    expectedStatus: 'Hallucinated',
    expectedScore: 0.0,
    query: 'Is alcohol reimbursable during official travel?',
    generated_answer: 'Alcohol expenses incurred during official company dinners are fully reimbursable up to 2,000 INR per day.',
    retrieved_documents: [
      {
        doc: 'hr_policy_reimb.txt',
        text: 'Section 2: Meal Allowance. Employees on official travel receive a daily meal allowance of 1,200 INR within India and 40 USD for international travel. Alcohol is not reimbursable under any circumstances.'
      },
      {
        doc: 'hr_policy_reimb.txt',
        text: 'Section 1: General Principles. Employees traveling for official business are reimbursed for economy class airfare, train fare, and pre-approved local transport. All expense claims must be submitted within 30 days.'
      }
    ],
    verification: {
      query: 'Is alcohol reimbursable during official travel?',
      answer: 'Alcohol expenses incurred during official company dinners are fully reimbursable up to 2,000 INR per day.',
      trust_score: 0.0,
      status: 'Hallucinated',
      explanation: 'Direct contradiction detected against hr_policy_reimb.txt: Policy explicitly states "Alcohol is not reimbursable under any circumstances". Strict factual violation.',
      claims: [
        {
          claim: 'Alcohol expenses incurred during official company dinners are fully reimbursable up to 2,000 INR per day',
          consensus: -1.0,
          evidence: [
            {
              doc: 'hr_policy_reimb.txt',
              text: 'Section 2: Meal Allowance. Employees on official travel receive a daily meal allowance of 1,200 INR within India and 40 USD for international travel. Alcohol is not reimbursable under any circumstances.',
              similarity: 0.887,
              label: 'CONTRADICTION',
              reason: 'Contradiction detected: Evidence explicitly mandates "Alcohol is not reimbursable under any circumstances". Negative polarity conflict.'
            }
          ]
        }
      ]
    }
  }
];

export const FROZEN_RESEARCH_METRICS = {
  rag_comparison: {
    dataset_queries: 77,
    model: 'TinyLlama-1.1B',
    conditions: [
      {
        id: 'cond_a',
        name: 'Condition A (Baseline RAG)',
        retrieval: 'TF-IDF (Top-2)',
        prompt: 'Standard Instructional',
        claims_per_answer: 1.53,
        truncation_pct: 1.3,
        hallucination_rate: 23.4,
        trusted_pct: 31.2,
        uncertain_pct: 45.5,
        mcnemar_p: 'Reference Baseline'
      },
      {
        id: 'cond_b',
        name: 'Condition B (Re-rank Only)',
        retrieval: 'SBERT Cross-Re-ranking',
        prompt: 'Standard Instructional',
        claims_per_answer: 1.58,
        truncation_pct: 2.6,
        hallucination_rate: 27.3,
        trusted_pct: 10.4,
        uncertain_pct: 62.3,
        mcnemar_p: 'p = 0.4531 (Not Sig)'
      },
      {
        id: 'cond_c',
        name: 'Condition C (Citation Prompt Only)',
        retrieval: 'TF-IDF (Top-2)',
        prompt: 'Strict [Section] Citation',
        claims_per_answer: 1.68,
        truncation_pct: 1.3,
        hallucination_rate: 22.1,
        trusted_pct: 23.4,
        uncertain_pct: 54.5,
        mcnemar_p: 'p = 1.0000 (Not Sig)'
      },
      {
        id: 'cond_d',
        name: 'Condition D (Combined Intervention)',
        retrieval: 'SBERT Re-ranking',
        prompt: 'Strict Citation Prompt',
        claims_per_answer: 1.92,
        truncation_pct: 3.9,
        hallucination_rate: 31.2,
        trusted_pct: 9.1,
        uncertain_pct: 59.7,
        mcnemar_p: 'p = 0.2863 (Not Sig)'
      },
      {
        id: 'cond_e',
        name: 'Condition E (Conciseness Constraint)',
        retrieval: 'TF-IDF (Top-2)',
        prompt: '1–2 Sentence Concise',
        claims_per_answer: 1.16,
        truncation_pct: 0.0,
        hallucination_rate: 24.7,
        trusted_pct: 16.9,
        uncertain_pct: 58.4,
        mcnemar_p: 'p = 1.0000 (Exact Binomial)'
      }
    ],
    key_finding: 'Reducing the claim-count/scoring confound (1.53 → 1.16 claims/answer, 0% truncation) did not reduce hallucination (23.4% in A vs 24.7% in E, McNemar p = 1.0000).'
  },
  trust_validation: {
    full_benchmark: {
      n: 130,
      binary_accuracy: 97.7,
      detection_precision: 97.1,
      detection_recall: 100.0,
      detection_f1: 98.5,
      supported_recall: 90.0,
      three_way_accuracy: 84.6,
      safety_violation_count: 0,
      safety_violation_total: 100,
      safety_violation_rate: '0.0%'
    },
    unseen_subset: {
      n: 42,
      held_out_n: 11,
      newly_constructed_n: 31,
      binary_accuracy: 100.0,
      detection_precision: 100.0,
      detection_recall: 100.0,
      detection_f1: 100.0,
      supported_recall: 100.0,
      three_way_accuracy: 88.1,
      safety_violation_count: 0,
      safety_violation_total: 36,
      safety_violation_rate: '0.0%'
    },
    score_distribution: {
      kruskal_wallis_h: 100.56,
      kruskal_wallis_p: '1.18 × 10^-21',
      eta_squared: 0.7743,
      supported_mean: 95.0,
      uncertain_mean: 31.94,
      hallucinated_mean: 3.12,
      note: 'Scores exhibit sharp discrete plateaus (100.0, 50.0, 0.0) reflecting evidence consensus states.'
    }
  }
};
