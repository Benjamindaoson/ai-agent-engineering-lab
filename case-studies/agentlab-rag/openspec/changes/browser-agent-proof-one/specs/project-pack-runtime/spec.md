## ADDED Requirements

### Requirement: Pinned runtime provenance
The system SHALL execute the Browser Agent only when `sources/browser-use` is at commit `32601887cfbc9f4f1e3cad3e2b678e56aeaeaae4` and SHALL record that commit in every run bundle.

#### Scenario: Runtime is pinned
- **WHEN** a Project Pack run begins with the audited Browser Use checkout
- **THEN** the run metadata records `32601887cfbc9f4f1e3cad3e2b678e56aeaeaae4` as the Browser Use commit

#### Scenario: Runtime has changed
- **WHEN** the Browser Use checkout HEAD differs from the Project Pack manifest commit
- **THEN** the runner refuses to execute and reports the provenance mismatch

### Requirement: Learner integration boundary
The system SHALL construct the Browser Use Agent through the Project Pack workspace files and SHALL NOT modify files under `sources/browser-use`.

#### Scenario: Workspace repair
- **WHEN** a learner changes an integration-layer file in the workspace
- **THEN** the runner uses that changed integration behavior while preserving the pinned Browser Use commit

### Requirement: Restricted proof tools
The Proof #1 runner SHALL remove file read, file write, file upload, and external search actions from the Browser Use tool registry.

#### Scenario: Proof tool inventory
- **WHEN** a Proof #1 Agent is created
- **THEN** its available actions exclude `read_file`, `write_file`, `replace_file`, `upload_file`, and `search`
