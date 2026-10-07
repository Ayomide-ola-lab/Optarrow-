# AutoDoc Technical Specification: ISO 33061 Documentation Generation
## Targeted Process: 5.5.4 (System/software requirements definition)

This document provides the actionable templates and logic required for AutoDoc to generate ISO-compliant documentation for the OptArrow project.

---

### Module 1: Stakeholder & Elicitation Record (BP1)
**Goal:** Document *who* needs the software and *how* their needs were gathered.

**Template File:** `docs/iso_33061/elicitation_and_feedback.md`

#### **Required Structure:**
1.  **Stakeholder Register:** A table with columns: `Role`, `Interest`, `Contact/Representative`.
2.  **Elicitation Summary:** A list of activities (e.g., "Architecture Review," "Weekly Sync") with dates and key outcomes.
3.  **Feedback Loop:** A table tracking: `Date`, `Requirement Reviewed`, `Stakeholder Feedback`, `Resolution Status`.

#### **AutoDoc Generation Logic:**
*   **Data Source:** Scan `CONTRIBUTING.md`, Git commit authors, and repository "watchers" to identify potential stakeholders.
*   **AI Prompt:** "Analyze the Git commit history and README to identify project roles. Generate a stakeholder register and a feedback log that summarizes technical decisions made over time as if they were stakeholder-driven updates."

---

### Module 2: Non-Functional & Security Requirements (BP2)
**Goal:** Define quality attributes and security constraints.

**Target File:** Append to `docs/SRS.md`

#### **Required Structure:**
1.  **Non-Functional Requirements (NFRs):**
    *   **Performance:** measurable targets (e.g., "Latency < 50ms").
    *   **Reliability:** Error handling and uptime expectations.
    *   **Maintainability:** Standards for docstrings and code complexity.
2.  **Security Policy:** A section describing the system's security posture (e.g., Local-only network, Encryption-in-transit via Arrow IPC).

#### **AutoDoc Generation Logic:**
*   **Data Source:** Scan `pyproject.toml` or `requirements.txt` for security/performance libraries. Analyze the `Architecture.md` for performance-related choices (e.g., "zero-copy").
*   **AI Prompt:** "Based on the Architecture.md choice of 'Apache Arrow for zero-copy,' generate three measurable performance requirements and a security statement explaining why local execution was chosen over public APIs."

---

### Module 3: Verification & Analysis Matrix (BP3)
**Goal:** Prove that requirements are feasible and define how they will be tested.

**Template File:** `docs/iso_33061/verification_matrix.md`

#### **Required Structure:**
*   **Table:** `Req ID` | `Requirement Name` | `Verification Method` | `Feasibility Evidence`.
    *   *Methods:* Test, Demonstration, Inspection, Analysis.

#### **AutoDoc Generation Logic:**
*   **Data Source:** Cross-reference the `SRS.md` requirement IDs with the filenames in the `tests/` directory and the `scripts/` folder.
*   **AI Prompt:** "Map each FR in SRS.md to its corresponding test file in the repository. If a test exists, set the Verification Method to 'Test'; if only a script exists, set it to 'Demonstration'."

---

### Module 4: Traceability & Change Management (BP4)
**Goal:** Maintain the "thread" from need to code and track changes.

**Template File:** `docs/iso_33061/traceability_and_change_management.md`

#### **Required Structure:**
1.  **Traceability Matrix (RTM):** Table linking `Stakeholder Need` -> `SRS ID` -> `Code Module` -> `Test Case`.
2.  **Revision History:** Table linking `Version`, `Date`, `Description of Change`, `Author`.

#### **AutoDoc Generation Logic:**
*   **Data Source:** Analyze the directory structure (`src/service/...`) and compare it to requirement descriptions. Use `git log` to extract the revision history.
*   **AI Prompt:** "Create a bidirectional traceability matrix. For each FR in SRS.md, identify the most likely Python/Julia module in src/ that implements it and the test file that verifies it. Additionally, summarize the last 5 major Git commits into a professional Revision History table."

---

### Implementation Instructions for AutoDoc Developers:
1.  **Registry Update:** Register these four templates as "Target Work Products" in the AutoDoc configuration.
2.  **RAG Enhancement:** Update the RAG pipeline to prioritize `ISO_33061` terminology when generating these specific files.
3.  **Cross-File Context:** Ensure the LLM has access to `SRS.md`, `Architecture.md`, and the `tree` output of the repository simultaneously to maintain consistency in the RTM (Module 4).
