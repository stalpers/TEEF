# TEEF conformance suite

This suite is a set of example packages, each paired with the result a conformant recipient must produce. It lets anyone check a TEEF implementation, in any language, against the [specification](../docs/architecture.md).

It serves three purposes:

- keeping the specification, schema, and examples consistent while the format evolves
- acceptance testing for the TEEF Python package
- letting other implementers show that their software follows the specification

The suite contains no validator. Implementations bring their own and run every case.

## Layout

```text
conformance/
  README.md
  case.schema.json          # JSON Schema for case.json
  tools/
    build_archives.py       # builds the ZIP archive cases
  0.1.0/                    # cases for schema version 0.1.0
    <case>/
      case.json             # description, input, context, expected result
      package/              # an unpacked package, or
      package.zip           # a package as a ZIP archive
```

Cases are grouped by schema version, so cases for one version stay available after a later, incompatible version is published.

Folder names follow three patterns:

- `valid-<description>`: a package that passes with no warnings beyond those listed.
- `warn-<description>`: a valid package that triggers exactly one warning.
- `<area>-<nn>-<description>`: a package that breaks one rule, named after that rule's ID. For example, `ref-06-unresolved-evidence-ref` breaks `TEEF-REF-06`.

## `case.json`

```json
{
  "description": "An evidenceRef points to an evidence ID that the package does not contain.",
  "input": "package",
  "expected": {
    "result": "invalid",
    "errors": ["TEEF-REF-06"],
    "warnings": []
  }
}
```

| Field | Meaning |
|---|---|
| `description` | What the case tests. |
| `input` | `package` for the `package/` folder, or `package.zip` for the archive. |
| `context` | Optional. What a recipient would know from outside the package. |
| `context.previousPackages` | Paths, relative to the case folder, to manifests the recipient has already received. Used for `supersedes` checks and package ID reuse. |
| `context.limits` | Archive limits the recipient applies: `maxArchiveBytes` (size of the ZIP file), `maxEntries` (number of entries), and `maxExpandedBytes` (total uncompressed size). Each case exceeds its limit whether or not the manifest entry is counted. |
| `context.intakeDate` | The date the recipient takes the package in for review, used for expiry (`TEEF-DATE-05`). When this field is absent, use the package's `generatedAt` date, so results do not depend on the day the suite runs. |
| `context.knownQuestionnaires` | Questionnaire `id` and `version` pairs the recipient knows. When this field is absent, the unknown-questionnaire check (`TEEF-ANS-12`) is not applied. |
| `expected.result` | `valid`, `invalid`, or `any`. `any` is used where the specification lets the recipient choose, such as rejecting or quarantining a URI that carries a token. |
| `expected.errors` | Rule IDs the recipient must report as errors. |
| `expected.warnings` | Rule IDs the recipient must report as warnings. |

[`case.schema.json`](case.schema.json) defines this format.

## Passing a case

An implementation passes a case when:

1. its result matches `expected.result`, where `any` accepts either result
2. it reports every rule ID in `expected.errors` and `expected.warnings`. On an `any` case, it may report the listed IDs as errors or as warnings
3. on a `valid` case, it reports no errors

It may report additional IDs, because one defect can trigger more than one finding. It may also report extra warnings on valid cases, because a recipient can apply stricter review policy than the specification requires.

## Errors and warnings

- An **error** is a broken MUST or MUST NOT rule. A package with any error is `invalid`.
- A **warning** is a finding the recipient must or should surface to a reviewer. A package with only warnings is `valid`.
- Every failure to validate against the JSON Schema is reported as `TEEF-SCHEMA-01`. Validators word schema errors differently, so the suite does not compare their messages or paths.

The [rule index](../docs/architecture.md#rule-index) marks each rule as tested by the suite (`yes`), enforced by the schema (`schema`), or not testable from a package (`no`).

## Running the schema checks

Schema validation must use JSON Schema Draft 2020-12 with `format` assertions enabled. Some validators skip `uri` and other format checks unless an extra package is installed. For example, the Python `jsonschema` library checks `uri` only when `rfc3987` or `rfc3986-validator` is installed. Without it, cases that rely on format checks pass when they should fail.

## Adding a case

1. Copy `0.1.0/valid-minimal/` to a new folder named as above.
2. Make one change, so the package breaks exactly one rule or triggers exactly one warning.
3. Write `case.json` with the rule ID you expect.
4. Validate `case.json` against `case.schema.json`.
5. If the case is a negative case for a rule other than `TEEF-SCHEMA-01`, check that its manifest still validates against the TEEF schema. Otherwise it breaks two rules.

Archive cases are defined in `tools/build_archives.py`, not by hand. Add the case to the script, write its `case.json`, and rebuild:

```text
python conformance/tools/build_archives.py
```

The script uses only the Python standard library. Its output is deterministic, so rebuilding unchanged cases produces identical files.

Files in this folder are stored byte-for-byte. Do not let an editor or Git change their line endings or encoding: digests in the manifests depend on the exact bytes.
