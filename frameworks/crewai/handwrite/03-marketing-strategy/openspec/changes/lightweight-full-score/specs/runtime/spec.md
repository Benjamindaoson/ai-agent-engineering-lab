# Runtime and Evaluation Specification

## ADDED Requirements

### Requirement: Configurable input
The CLI MUST accept a JSON input file and validate the required marketing fields before making external calls.

#### Scenario: Valid custom input
- **WHEN** the user runs with `--input inputs.example.json`
- **THEN** the run uses the file values and writes to the requested output directory.

#### Scenario: Missing required input
- **WHEN** a required field is empty or missing
- **THEN** the CLI exits non-zero with the field name in the error.

### Requirement: Isolated output
Each run MUST write to its configured output directory and clear only known generated files before starting.

#### Scenario: Reusing an output directory
- **WHEN** a previous run left a generated JSON file
- **THEN** the next run removes that known file before kickoff.

### Requirement: Independent evaluation cases
The evaluator MUST run or load one output directory per case and MUST validate the case manifest against that case's inputs.

#### Scenario: Three cases
- **WHEN** the evaluator processes `cases.json`
- **THEN** it reports three distinct case directories and does not reuse one global output directory.

### Requirement: Traceable research
Research output MUST contain source names and at least one URL for externally verified claims, while marking inference separately.

#### Scenario: Research report
- **WHEN** a research report is generated
- **THEN** it contains a source section with URLs and evidence levels.
