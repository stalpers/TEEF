# Contributing

The [architecture](architecture.md) defines exchange semantics. The [`schema/`](schema/) directory contains versioned JSON Schemas. The [`examples/`](examples/) directory contains fictional packages that illustrate those semantics. The [conformance suite](../conformance/README.md) contains test packages with the result a conformant recipient must produce.

## Proposing a change

1. Describe the interoperability problem using an example a publisher would produce and a recipient would consume.
2. Update the semantics, schema, affected examples, and conformance cases together. Keep existing versioned drafts and their conformance cases available when proposing incompatible changes.
3. Give every new MUST, MUST NOT, SHOULD, or SHOULD NOT rule a new rule ID and a row in the [rule index](architecture.md#rule-index). Never renumber or reuse an ID. When a rule is removed, retire its ID.
4. Add or update conformance cases for every rule ID you add or change, as described in the [suite's README](../conformance/README.md#adding-a-case). Each negative case breaks exactly one rule.
5. Use two-space indentation for JSON, stable identifiers, and synthetic sample data. Preserve attachment bytes and refresh their declared digest if they change.
6. Check the schema against the Draft 2020-12 meta-schema. Validate the example using a Draft 2020-12 validator with `format` assertions for `date`, `date-time`, `uri`, and `uuid` enabled. Then run the conformance suite.
