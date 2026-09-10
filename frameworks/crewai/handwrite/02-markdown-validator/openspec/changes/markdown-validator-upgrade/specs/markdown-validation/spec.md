## ADDED Requirements

### Requirement: Validate one Markdown path without mutation
The validation Tool SHALL accept one file path, inspect that file, and never write to it.

#### Scenario: Existing Markdown file
- **WHEN** the Tool receives an existing `.md` file
- **THEN** it returns a validation report and the file contents remain unchanged

#### Scenario: Missing file
- **WHEN** the Tool receives a path that does not exist
- **THEN** it returns a clear error identifying the missing path

#### Scenario: Non-Markdown file
- **WHEN** the Tool receives an existing file whose suffix is not `.md`
- **THEN** it returns a clear non-Markdown warning without modifying the file

### Requirement: Report the minimum Markdown issue set
The validation Tool SHALL report line-aware findings for empty files, heading-level jumps, empty headings, duplicate headings, unclosed fenced code blocks, trailing spaces, bare URLs, and images with empty alt text.

#### Scenario: File contains required issue types
- **WHEN** the Tool scans a sample containing those Markdown issues
- **THEN** the report includes the issue type and one-based line number for each finding

#### Scenario: Clean Markdown file
- **WHEN** the Tool scans a valid non-empty Markdown file with none of the supported issues
- **THEN** the report states that no Markdown validation issues were found
