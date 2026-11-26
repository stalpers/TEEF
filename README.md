# TPRM Evidence Exchange Format (TEEF)

TEEF is an open, machine-readable format for exchanging third-party risk management (TPRM) questionnaire responses and evidence between suppliers and the organisations that assess them.

A supplier generates one package from the systems it already uses: a spreadsheet, a trust centre, a questionnaire database, or a TPRM tool. The buyer or assessor imports that package into its own review workflow, instead of matching answers, certificates and reports that arrived through separate channels.

**Status:** Draft 0.1.0. The format may still change in incompatible ways before 1.0.

## What a package carries

A TEEF package is a JSON manifest, plus any evidence files in their original format:

```text
manifest.json
evidence/
  subprocessors.json
```

The manifest identifies the supplier, the assessed legal entity and service, and their operating scope. It can carry:

- **Questionnaire responses**, keyed by questionnaire URI, version and question ID. Buyers keep their own questionnaires. Answers can be mapped to other questionnaires or control frameworks, so an approved answer can be reused.
- **Evidence** such as certificates, assurance reports, bridge letters, penetration tests, policies and subprocessor lists, with issuer, scope, validity and coverage.
- **Structured details** for SOC 2 and similar reports (opinion, exceptions, carve-outs, user entity controls) and for certificates (standard, certificate number, accreditation, last audit, register link).
- **Integrity and security bindings**: SHA-256 digests of files, an optional detached signature and trusted timestamp, and optional whole-package encryption.

See the [example package](docs/examples/supplier-package/manifest.json) for a complete manifest.

## Repository contents

| Path | Contents |
|---|---|
| [`docs/background.md`](docs/background.md) | Why TEEF exists and where it fits |
| [`docs/architecture.md`](docs/architecture.md) | The specification, with a numbered rule index |
| [`docs/schema/`](docs/schema/) | JSON Schema (Draft 2020-12) for the manifest |
| [`docs/examples/`](docs/examples/) | A fictional example package |
| [`conformance/`](conformance/README.md) | Test packages with the result a conformant recipient must produce |
| [`docs/contribute.md`](docs/contribute.md) | How to propose a change |
| [`design/`](design/) | Design notes for work on the format and suite |

## Validating a package

1. Validate `manifest.json` against the [schema](docs/schema/tprm-evidence-exchange-0.1.0.schema.json) with a Draft 2020-12 validator, with `format` assertions enabled.
2. Apply the package-level rules in the [specification](docs/architecture.md#validation-and-trust-boundaries). These cover references, dates, digests, archive safety, and the findings a reviewer should see.

The [conformance suite](conformance/README.md) lets you check an implementation against both steps. Each case names the rule IDs it expects, such as `TEEF-REF-06`, so a failing case points to the exact rule.

## Roadmap

- **Now:** finalise the 0.x data model and conformance suite.
- **Next:** a Python package for generating, reading and modifying TEEF packages.
- **Then:** adapters for open-source GRC and TPRM tools.

## Contributing

Issues and pull requests are welcome. Read [`docs/contribute.md`](docs/contribute.md) first: changes update the specification, schema, examples and conformance cases together, and every rule keeps a stable ID.

All sample data in this repository is fictional and uses `.example` domains.

## License

Copyright 2026 TEEF contributors.

Licensed under the [Apache License, Version 2.0](LICENSE).
