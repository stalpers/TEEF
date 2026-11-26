# TPRM Evidence Exchange Format

**Draft 0.1.0**

The format carries third-party risk management (TPRM) questionnaire responses and evidence from a publisher to a recipient. A supplier can generate the same package from a spreadsheet, a trust centre, a questionnaire database, or a TPRM tool. Supplier adapters, APIs, and libraries are outside this draft.

The [background and rationale](background.md) describe the exchange problem and how TEEF fits into supplier and recipient workflows.

The [JSON Schema](schema/tprm-evidence-exchange-0.1.0.schema.json) defines the manifest structure. This document defines package layout, field meanings, checks that span fields or files, and optional security bindings. The [example manifest](examples/supplier-package/manifest.json) uses fictional data and illustrative URLs. It is unencrypted so that it can be read directly. A real package carrying the same SOC 2 details would be confidential, and should be encrypted as described in [Whole-package encryption](#whole-package-encryption).

## Conventions and roles

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals, as shown here.

- A **publisher** assembles and releases a package. Requirements on the publisher apply to the software and process that produce the package.
- A **recipient** receives, validates, and imports a package. Requirements on the recipient apply to its intake software and review process.

Rationale, examples, and notes are non-normative.

Each requirement carries a rule ID, such as `TEEF-REF-06`, so that implementations, test cases, and bug reports can cite it. IDs are never renumbered or reused. The [rule index](#rule-index) lists every rule. The [conformance suite](../conformance/README.md) tests the rules a recipient can check from package content.

- **TEEF-PKG-01** A requirement on package content binds the publisher. When a recipient detects that a package breaks a MUST or MUST NOT requirement on package content, it MUST reject the package, unless the rule says otherwise.

## Package layout

```text
manifest.json
evidence/                  # present when files are included
  subprocessors.json
manifest.jws               # optional detached signature
manifest.tst               # optional trusted timestamp
```

- **TEEF-PKG-02** The manifest MUST be UTF-8 encoded JSON without a byte order mark.
- **TEEF-PKG-03** The manifest MUST NOT contain duplicate member names.
- **TEEF-PKG-04** When a package is exchanged as a single file, the publisher MUST use a ZIP archive with `manifest.json` at its root.
- **TEEF-PKG-05** ZIP entries MUST use the same relative paths as the manifest.
- The archive MAY include an `evidence/` directory entry.
- A manifest that contains only inline text or external references MAY be exchanged by itself when no signature or timestamp files are needed.

*Rationale:* A single JSON file with Base64 attachments would simplify delivery while increasing payload size and putting every file inside the JSON document. Keeping files alongside the manifest preserves their original bytes and lets recipients hash or inspect them separately.

## Whole-package encryption

A publisher MAY encrypt the entire ZIP, for example when the package contains an NDA-only SOC 2 report. Encryption protects the manifest, questionnaire answers, attachments, and any signature or timestamp files inside the archive.

When a publisher encrypts a package:

1. **TEEF-SIG-01** The publisher MUST assemble the ZIP, including the manifest, attachments, and any signature or timestamp files, before encryption.
2. **TEEF-SIG-02** The publisher MUST wrap the ZIP in a compact JWE for exactly one recipient, using the recipient's public encryption key obtained through an authenticated channel.
3. **TEEF-SIG-03** The protected header MUST contain `alg: RSA-OAEP-256`, `enc: A256GCM`, `cty: application/zip`, and `kid`.
4. **TEEF-SIG-04** The recipient MUST decrypt and authenticate the JWE with its private key before opening the ZIP.
5. **TEEF-SIG-05** The recipient MUST then validate the manifest, attachment digests, and any inner signature or timestamp as described in [Validation and trust boundaries](#validation-and-trust-boundaries) and [Optional signature and timestamp](#optional-signature-and-timestamp).

[JWE compact serialization](https://www.rfc-editor.org/rfc/rfc7516.html#section-7.1), [JOSE algorithms](https://www.rfc-editor.org/rfc/rfc7518)

## Core model

| Field | Meaning |
|---|---|
| `schemaVersion` | Exact format version. |
| `packageId` | UUID identifying an immutable manifest and its declared attachments. Replaying the same snapshot under the same ID is valid. |
| `supersedes` | OPTIONAL. The package ID of an earlier snapshot. The recipient MAY process this package independently of the earlier one. |
| `publisher` | Organisation releasing the package. The OPTIONAL URI identifier helps recipients match agreed identities. |
| `subject` | A single assessed legal entity, an optional service, and an optional structured `scope`. The subject identifies the intended assessment scope. See [Subject scope](#subject-scope). |
| `generatedAt` | Publisher-asserted generation time. |
| `questionnaires` | One or more sets of responses, keyed by questionnaire URI and version. The pair identifies the question definitions, types, choices, and units. |
| `evidence` | One or more items with package-local IDs, provenance where known, and exactly one content representation. |

- **TEEF-SCHEMA-01** The recipient MUST validate the manifest against the JSON Schema for its `schemaVersion`, with JSON Schema `format` assertions enabled.
- **TEEF-SCHEMA-02** The recipient MUST report an unsupported `schemaVersion` instead of processing the package.
- **TEEF-ID-01** The publisher MUST assign a new `packageId` to each distinct snapshot and MUST NOT reuse an ID for a different snapshot.
- **TEEF-ID-02** A recipient that sees a `packageId` reused for a different snapshot MUST treat it as an integrity error.
- **TEEF-REF-01** When present, `supersedes` MUST identify an earlier package from the same publisher for the same subject.
- **TEEF-SCOPE-01** The publisher SHOULD supply the service for service-specific exchanges.
- **TEEF-PKG-06** `generatedAt` MUST be an RFC 3339 timestamp in UTC using `Z`.
- **TEEF-ANS-01** For a buyer-defined questionnaire, the publisher MUST use the stable URI assigned by the buyer.
- **TEEF-PKG-07** A package MUST contain questionnaire responses, evidence, or both.
- **TEEF-ANS-02** The recipient MUST NOT interpret an omitted question as `unknown`, `notApplicable`, or `withheld`.

A partial questionnaire exchange is valid. An omitted question has no response in this snapshot.

### Subject scope

The OPTIONAL `subject.scope` object describes the footprint of the assessed entity or service, so a recipient can compare it with the scope of certificates and other evidence.

| Field | Meaning |
|---|---|
| `countries` | ISO 3166-1 alpha-2 codes, in upper case, for the countries where the service is delivered, operated, or supported, or where its data is processed. |
| `components` | The main parts of the service, such as storage, a management console, or billing. |
| `description` | Free text for scope that the other fields do not capture. |

- **TEEF-SCOPE-02** A subject scope MUST contain at least one field.
- **TEEF-SCOPE-03** The publisher SHOULD list every country where the service is operated or supported, or where its data is processed, including remote support locations. A narrower list makes the comparison with evidence scope misleading.
- **TEEF-SCOPE-04** The recipient SHOULD check the subject scope against its own knowledge, such as the contract and the data flows it observes.
- **TEEF-SCOPE-05** The subject scope is the publisher's own statement. The recipient MUST NOT treat it as independently verified.

The recipient compares the subject scope with the coverage of certificates and assurance reports:

- **TEEF-SCOPE-06** When a certificate's `certification` or an assurance report's `assuranceReport` carries `organizations`, the recipient SHOULD surface a subject organisation that is not among them.
- **TEEF-SCOPE-07** The recipient SHOULD compare organisations by `identifier` when both sides carry one.
- **TEEF-SCOPE-08** When either side lacks an `identifier`, the recipient SHOULD show both names to the reviewer and not conclude that they differ.
- **TEEF-SCOPE-09** When both the subject scope and a certificate or assurance report carry `countries`, the recipient SHOULD surface every subject country that the evidence does not list.

*Note:* Countries and legal entity identifiers can be compared automatically. Components and free-text scope usually need a reviewer, unless both sides use agreed names.

### Responses

| Status | Meaning |
|---|---|
| `answered` | The response carries an `answer`: a JSON string, boolean, number, or array of distinct string choice codes. Supporting `evidenceRefs` are OPTIONAL. |
| `reference` | The evidence identified by `evidenceRefs` supplies the answer. An OPTIONAL `locator` points a reviewer to a relevant page, heading, or section. |
| `unknown` | The publisher cannot determine the answer. |
| `notApplicable` | The question does not apply to the stated subject. |
| `withheld` | The publisher has chosen to withhold the answer from this exchange. |

Every status MAY carry an explanatory `note`.

- **TEEF-ANS-03** An `answered` response MUST carry an `answer`.
- **TEEF-ANS-04** A `reference` response MUST carry `evidenceRefs`.
- **TEEF-ANS-05** A `reference` response MUST NOT carry an `answer`.
- **TEEF-ANS-06** Responses with `unknown`, `notApplicable`, or `withheld` MUST NOT carry an `answer` or `evidenceRefs`.
- **TEEF-ANS-07** The publisher and recipient MUST preserve `false` and `0` as answer values and MUST NOT treat them as absent.
- **TEEF-ANS-08** The recipient MUST match on questionnaire URI, version, and question ID before applying a response to a receiving assessment.
- **TEEF-ANS-09** The recipient SHOULD interpret choice codes and units using the question definition.

#### Question snapshot

A response MAY carry `questionText`, the text of the question as the publisher received and answered it. It lets a recipient detect a question that changed without a new questionnaire version, and lets a reviewer read the package without the questionnaire definition.

- **TEEF-ANS-10** When the publisher supplies `questionText`, it MUST reproduce the question as received, without paraphrasing.

The questionnaire definition identified by URI and version remains authoritative. A recipient that has the definition compares the snapshot with it, as described in [Validation and trust boundaries](#validation-and-trust-boundaries).

#### Mappings

A response MAY carry `mappings`: identifiers of related questions or controls in other schemes. Each mapping names a `scheme` URI, an OPTIONAL scheme `version`, the `id` within that scheme, and an OPTIONAL `relationship`. A scheme can be a control framework, another buyer's questionnaire, or the publisher's own answer library. The format does not prescribe any scheme.

Mappings let a recipient recognise an answer it has already reviewed under a different questionnaire, and let a publisher reuse one approved answer across several buyers' questionnaires.

The `relationship` states how the scope of this response's question compares with the scope of the mapped item:

| Relationship | Meaning |
|---|---|
| `equivalent` | Both ask for the same thing. An answer to one answers the other. |
| `subset` | This question covers only part of what the mapped item covers. |
| `superset` | This question covers everything the mapped item covers, and more. |
| `intersects` | The two overlap, but neither contains the other. |

A mapping is the publisher's assertion about how the response relates to the identified question or control. It does not make the response part of another questionnaire. When `relationship` is omitted, the mapping asserts only that the items are related.

- **TEEF-MAP-01** When `relationship` is omitted, the recipient MUST NOT assume the items are equivalent.
- **TEEF-MAP-02** The recipient MUST NOT apply a response to a questionnaire other than the one it is listed under unless the reviewer confirms it, or the mapping's `relationship` is `equivalent` and the recipient's policy explicitly accepts that publisher's mappings for that scheme.
- The recipient MAY ignore mappings to schemes it does not recognise.

*Note:* An answer to a broader question does not always answer a narrower one. A "yes" to "Is data encrypted at rest and in transit?" implies a "yes" for encryption at rest, but a numeric or free-text answer usually does not carry over. This is why only `equivalent` mappings qualify for policy-based reuse.

### Evidence

Each evidence item uses one content mode: `inline` for plain text, `file` for an included text or binary file, or `external` for an HTTPS reference.

- **TEEF-EV-01** For an included file, `sha256` MUST be the lowercase hexadecimal SHA-256 digest of the exact file bytes.
- **TEEF-URI-01** An external reference MUST use HTTPS.
- **TEEF-URI-02** An external URI MUST NOT contain user information (such as `user:password@`), bearer tokens, or other credentials. The schema rejects user information in the authority. Other credentials in a URI are handled under TEEF-URI-06, not TEEF-PKG-01, so the recipient chooses whether to reject or quarantine.
- The publisher MAY include a digest for an external item when it knows the exact bytes. Without that digest, the package records the link as supplied.
- **TEEF-EV-02** Without a digest, the recipient MUST NOT assume the target of an external reference is unchanged.

Evidence metadata describes the artefact itself. A certificate may cover fewer services or locations than the package subject. For a certificate, the scope is REQUIRED and is carried in `certification.scope`, as described in [Certificate details](#certificate-details).

- **TEEF-EV-03** The publisher SHOULD supply the original `issuer` and `scope` where known.
- `issuedOn` is the issuance date. `validFrom` and `validUntil` delimit validity. `coveragePeriod` describes the period assessed by an artefact. These fields use calendar dates, with inclusive bounds for validity and coverage.
- `collectedAt` gives the publisher's collection time.
- **TEEF-EV-04** Omitted metadata conveys no assertion. The recipient MUST NOT infer a value for an omitted field.

#### Evidence kinds

The `kind` field classifies the artefact so a recipient can route it to the right review step. The table also says how the common metadata fields apply to each kind.

| Kind | Use for | Metadata guidance |
|---|---|---|
| `certificate` | A certificate or attestation of compliance issued against a standard, such as ISO/IEC 27001, ISO 22301, or a PCI DSS Attestation of Compliance. | `issuer` is the certification body or assessor. `validFrom` and `validUntil` are the certificate's validity. The certified scope and any certificate number go in the REQUIRED `certification` object, not in the common `scope` field. |
| `assurance-report` | An independent auditor's report on controls, such as SOC 1, SOC 2, SOC 3, ISAE 3402, or ISAE 3000. | `issuer` is the audit firm. `issuedOn` is the report date. `coveragePeriod` is the period examined. For a point-in-time report, `from` and `to` are both the as-of date. |
| `bridge-letter` | A statement by the service organisation covering the gap between the end of an assurance report's coverage and a later date. | `issuer` is the service organisation. `coveragePeriod` is the gap period. |
| `penetration-test` | A report, executive summary, or attestation letter from a penetration test. | `issuer` is the testing firm or internal team. `coveragePeriod` is the testing window. `scope` names the systems tested. |
| `continuity-test` | Results or a summary of a business continuity or disaster recovery test or exercise. | `coveragePeriod` is the test date or dates. `scope` names the services or sites exercised. |
| `architecture-diagram` | An architecture, network, or data-flow diagram of the subject's systems or service. | `issuer` is the organisation that owns the diagram. `issuedOn` is the date of the depicted state. `scope` names the systems, environments, or data flows shown. |
| `policy` | A policy, standard, or procedure, or a summary of one. | `issuer` is the organisation that owns the document. `issuedOn` is its approval date. |
| `insurance-certificate` | A certificate of insurance, such as cyber or professional liability cover. | `issuer` is the insurer or broker. `validFrom` and `validUntil` are the policy period. `scope` states the cover type. |
| `agreement` | A contractual or legal document, such as a data processing agreement, standard contractual clauses, or standard terms. | `validFrom` is the effective date. `validUntil` is the end date, when there is one. |
| `subprocessor-list` | A list of subprocessors for the subject or service. | `validFrom` is the date the list takes effect. |
| `other` | Any artefact that no other kind describes. | The `title` describes the artefact. |

- **TEEF-EV-05** The publisher SHOULD follow the metadata guidance in the table when it supplies those fields.
- **TEEF-REF-02** When the bridged report is in the package, a bridge letter SHOULD reference it through `relatedEvidence` with `bridges`.
- **TEEF-EV-06** When the bridged report is not in the package, the bridge letter's `title` or `scope` SHOULD identify the report.
- **TEEF-EV-07** The `scope` of an `insurance-certificate` SHOULD state the cover type.
- **TEEF-EV-08** The publisher SHOULD use a more specific kind than `other` when one applies.
- **TEEF-EV-09** The `title` of an `other` item SHOULD describe the artefact.

#### Related evidence

An evidence item MAY carry `relatedEvidence`: references to other evidence items in the same package. Each reference names an `evidenceId` and a `relationship`, which states what this item does to the referenced one:

| Relationship | Meaning |
|---|---|
| `bridges` | This item extends the coverage of the referenced assurance report to a later date. |
| `summarizes` | This item is a summary or extract of the referenced item, such as a policy summary or a penetration test executive summary. |
| `supplements` | This item adds information to the referenced item without replacing it, such as a management response to report exceptions. |

- **TEEF-REF-03** A `bridges` reference MUST appear only on a `bridge-letter`.
- **TEEF-REF-04** A `bridges` reference MUST reference an `assurance-report`.
- **TEEF-REF-05** An evidence item MUST NOT reference itself through `relatedEvidence`.
- **TEEF-DATE-01** For a `bridges` reference, the bridge letter's `coveragePeriod.from` SHOULD be the day after the report's `coveragePeriod.to`.
- **TEEF-DATE-02** When a bridge letter's coverage does not begin the day after the bridged report's coverage ends, the recipient SHOULD surface the gap or overlap to the reviewer.

#### Assurance report details

An `assurance-report` item MAY carry an `assuranceReport` object that records the report's conclusions in structured form. The common fields keep their meaning: `issuer` is the audit firm, `issuedOn` is the report date, and `coveragePeriod` is the period examined.

| Field | Meaning |
|---|---|
| `standard` | REQUIRED. The reporting standard or framework, such as `SOC 2` or `ISAE 3402`. |
| `reportType` | `type-1` for a report on control design at a point in time. `type-2` for a report on design and operating effectiveness over a period. Omit it for reports without types, such as SOC 3. |
| `criteria` | The criteria or control objectives covered, such as the Trust Services Criteria categories `Security` and `Availability`. |
| `organizations` | The legal entities whose system the report covers, with identifiers where known. |
| `countries` | ISO 3166-1 alpha-2 codes, in upper case, for the countries where the system covered by the report operates. |
| `opinion` | The auditor's opinion: `unmodified`, `qualified`, `adverse`, or `disclaimer`. |
| `exceptions` | Deviations reported by the auditor. Each item has a `description` and MAY carry a control or criterion `reference` and the service organisation's `managementResponse`. |
| `subserviceOrganizations` | Subservice organisations named in the report. Each item has an `organization`, a `method` of `carve-out` or `inclusive`, and OPTIONAL `services`. |
| `userEntityControls` | Complementary user entity controls: controls the report assumes the recipient operates. |

An omitted list conveys no assertion. An empty list asserts that the report names none. For example, `"exceptions": []` states that the report notes no exceptions. These fields summarise the report. They do not replace it, and the report itself remains authoritative.

- **TEEF-AR-01** Evidence kinds other than `assurance-report` MUST NOT carry `assuranceReport`.
- **TEEF-AR-02** When `reportType` is `type-1`, `coveragePeriod.from` and `coveragePeriod.to` MUST be the same date.
- **TEEF-AR-03** When `reportType` is `type-2`, `coveragePeriod.from` MUST be earlier than `coveragePeriod.to`.
- **TEEF-AR-04** The publisher MUST copy these fields from the report without reinterpretation.
- **TEEF-AR-05** `organizations` and `countries` are a structured reading of the system boundary in the report's system description, and MUST NOT go beyond it. When they disagree with the report, the report takes precedence.
- **TEEF-AR-06** Countries where only a carved-out subservice organisation operates are outside the boundary and MUST NOT be listed in `countries`.
- **TEEF-AR-07** The recipient SHOULD surface to the reviewer an opinion other than `unmodified`.
- **TEEF-AR-08** The recipient SHOULD surface reported exceptions to the reviewer, whatever the opinion. An `unmodified` opinion can coexist with exceptions that the auditor did not consider material.
- **TEEF-AR-09** The recipient SHOULD surface any carved-out subservice organisation to the reviewer.
- **TEEF-AR-10** The recipient SHOULD surface any complementary user entity controls to the reviewer.
- **TEEF-AR-11** These fields move report content into the manifest, so when the report is confidential, its details are too. The publisher SHOULD then encrypt the package as described in [Whole-package encryption](#whole-package-encryption), or omit the fields.

#### Certificate details

A `certificate` item carries a `certification` object that records what the certificate states, such as for an ISO/IEC 27001 certificate. The certified scope belongs in `certification.scope`, so the scope is recorded in one place only. The other common fields keep their meaning: `issuer` is the certification body, `issuedOn` is the issue date, and `validFrom` and `validUntil` are the certificate's validity.

| Field | Meaning |
|---|---|
| `standard` | REQUIRED. The standard and edition certified against, such as `ISO/IEC 27001:2022`. |
| `certificateNumber` | The number or registry identifier the certification body or scheme assigned to the certificate. REQUIRED when the certificate carries one. |
| `scope` | REQUIRED. The certified scope, as worded on the certificate. |
| `organizations` | The legal entities the certificate covers, with identifiers where known. |
| `countries` | ISO 3166-1 alpha-2 codes, in upper case, for the countries the certificate covers. |
| `accreditationBody` | The body that accredits the certification body, such as a national accreditation service. |
| `sites` | The certified sites or locations, as listed on the certificate or its annex. |
| `statementOfApplicability` | The version and date of the Statement of Applicability cited on the certificate. |
| `lastAudit` | The `date` and `type` of the most recent audit. ISO-style certification uses `initial`, `surveillance`, or `recertification`. Schemes that reassess in full each year, such as PCI DSS, use `annual-assessment`. |
| `verificationUri` | An HTTPS link to the certification body's public register entry for this certificate. |

The scope lets a reviewer check that the certificate covers the package subject. The certificate number lets a reviewer confirm the certificate against the certification body's register. The certificate itself remains authoritative. The recipient compares `organizations` and `countries` with the subject scope as described in [Subject scope](#subject-scope).

- **TEEF-CERT-01** A `certificate` item MUST carry a `certification` object.
- **TEEF-CERT-02** Evidence kinds other than `certificate` MUST NOT carry `certification`.
- **TEEF-CERT-03** A certificate MUST NOT carry the common `scope` field.
- **TEEF-CERT-04** A `statementOfApplicability` MUST contain at least one of `version` and `date`.
- **TEEF-CERT-05** The publisher MUST copy these fields from the certificate or the certification body's records without reinterpretation.
- **TEEF-CERT-06** When the certificate or the scheme's register shows a number or identifier, the publisher MUST supply it in `certificateNumber`. Some attestations, such as a PCI DSS Attestation of Compliance, carry none. The publisher then omits the field.
- **TEEF-CERT-07** A certificate without a `certificateNumber` cannot be checked against a register by number. The recipient SHOULD surface this to the reviewer.
- **TEEF-CERT-08** `organizations` and `countries` are a structured reading of the certified scope, and MUST NOT go beyond it. When they and `scope` disagree, `scope` takes precedence.
- **TEEF-CERT-09** A certificate without an `accreditationBody` may be unaccredited. The recipient SHOULD surface this to the reviewer.
- **TEEF-CERT-10** ISO management system certificates normally require a surveillance audit each year, and schemes using `annual-assessment` reassess each year. When `lastAudit.date` is more than 12 months before `generatedAt`, the recipient SHOULD surface this to the reviewer.
- **TEEF-CERT-11** The `verificationUri` is an external reference and is not dereferenced during validation (TEEF-URI-04). Where its policy allows, the recipient SHOULD check the register entry to confirm the certificate's status, because a certificate can be suspended or withdrawn before `validUntil`.

Each evidence file keeps its existing format. For example, a structured subprocessor list can travel as a JSON attachment, with its field definitions agreed separately.

## Validation and trust boundaries

The recipient validates the manifest against the schema (TEEF-SCHEMA-01), rejects packages that break content rules (TEEF-PKG-01), and applies the following package-level rules.

**Identifiers and references**

- **TEEF-ID-03** The recipient MUST reject a package in which evidence IDs, questionnaire ID and version pairs, question IDs within a questionnaire, or declared file paths are not unique.
- **TEEF-REF-06** The recipient MUST reject a package containing an `evidenceRef` or `relatedEvidence` reference that does not resolve to an evidence item in the same package.
- **TEEF-REF-07** The recipient MUST reject a package whose `supersedes` value equals its own `packageId`.
- **TEEF-REF-08** When the superseded package is available, the recipient MUST verify that its publisher and subject match, and MUST reject the package if they differ.

**Dates and answers**

- **TEEF-DATE-03** The recipient MUST reject a package in which `validFrom` is later than `validUntil`, or `coveragePeriod.from` is later than `coveragePeriod.to`.
- **TEEF-DATE-04** The recipient MUST NOT reject a package solely because evidence has expired or has no stated scope.
- **TEEF-DATE-05** The recipient SHOULD present evidence to the reviewer as expired when its `validUntil` is before `generatedAt`, or before the date the recipient takes the package in for review. Evidence can expire between generation and intake.
- **TEEF-EV-10** The recipient SHOULD present evidence without a stated scope to the reviewer. For a certificate, the stated scope is `certification.scope`.
- **TEEF-ANS-11** When the questionnaire definition is available, the recipient SHOULD check each answer's type and choice codes against it.
- **TEEF-ANS-12** When the questionnaire URI or version is unknown to the recipient, it MUST surface this to the reviewer.
- **TEEF-ANS-13** The recipient MUST NOT apply answers to an unknown questionnaire or version automatically.
- **TEEF-ANS-14** When a response's `questionText` differs from the available question definition, the recipient SHOULD surface the difference before applying the response.

**Attachments and archives**

- **TEEF-EV-11** The recipient MUST verify that each declared file exists at its declared path and matches its declared digest, and MUST reject the package otherwise.
- **TEEF-ARC-01** The recipient MUST reject a package containing files that the manifest does not declare, other than `manifest.jws`, `manifest.tst`, and an `evidence/` directory entry.
- **TEEF-ARC-02** The recipient MUST reject archive entries that use absolute paths or path traversal.
- **TEEF-ARC-03** The recipient MUST reject archive entries that use reserved device filenames, such as `CON`, `NUL`, or `COM1`, with or without an extension.
- **TEEF-ARC-04** The recipient MUST reject archive entries that are symbolic or hard links.
- **TEEF-ARC-05** The recipient MUST reject duplicated archive entries.
- **TEEF-ARC-06** The recipient MUST reject archive entries that collide with another entry when compared case-insensitively.
- **TEEF-ARC-07** The recipient MUST enforce limits on archive size, entry count, and total expanded size before extracting attachments. The recipient sets these limits.
- **TEEF-ARC-08** The recipient SHOULD apply its file inspection policy to every attachment.

**Untrusted input**

- **TEEF-URI-03** The recipient MUST treat package data, URLs, and attachment contents as untrusted at intake.
- **TEEF-URI-04** The recipient MUST NOT dereference external references during package validation.
- **TEEF-URI-05** Any later retrieval of an external reference MUST follow the recipient's network and access policy.
- **TEEF-URI-06** The recipient SHOULD reject or quarantine an external URI that appears to carry credentials or bearer tokens, for example in its query string.

**Distribution and retention**

- **TEEF-DIST-01** The publisher MUST include only material it is permitted to disclose to the recipient.
- **TEEF-DIST-02** Where redistribution is restricted, the publisher SHOULD use access-controlled external references.
- **TEEF-DIST-03** The recipient SHOULD apply its distribution and retention policy to both the manifest and the files.
- **TEEF-DIST-04** The recipient SHOULD retain the received snapshot and its verification result according to its evidence policy.

## Optional signature and timestamp

These draft bindings protect package bytes while keeping the payload schema independent of cryptographic tooling. A signature and a timestamp are each OPTIONAL for the publisher. The recipient's policy determines which of them are REQUIRED for a given exchange.

| Control | Binding |
|---|---|
| **Public-key signature** | `manifest.jws` is a detached compact JWS over the exact `manifest.json` bytes. After digest verification, the signature binds the manifest and its declared file bytes. |
| **Trusted timestamp** | `manifest.tst` is an RFC 3161 `TimeStampToken` over the exact `manifest.json` bytes. The token establishes an upper bound on when those bytes existed. |

- **TEEF-SIG-06** `manifest.jws` MUST be a detached compact JWS over the exact `manifest.json` bytes, using standard Base64url payload encoding, with the payload segment left empty in the stored JWS.
- **TEEF-SIG-07** The JWS protected header MUST carry `alg: PS256` and `kid`.
- **TEEF-SIG-08** The recipient MUST resolve `kid` only through its trusted publisher key configuration.
- **TEEF-SIG-09** `manifest.tst` MUST be a DER-encoded RFC 3161 `TimeStampToken` with a SHA-256 message imprint over the exact `manifest.json` bytes.
- **TEEF-SIG-10** The recipient MUST verify the timestamp's imprint, the token signature, and that the timestamp authority is trusted.
- **TEEF-SIG-11** Parties MUST use separate keys for signing and encryption. The parties define key rotation and revocation.
- **TEEF-SIG-12** The recipient MUST reject a package containing an invalid signature or timestamp, whether or not its policy requires that proof.
- **TEEF-SIG-13** The recipient MUST reject a package that lacks a proof its policy requires.
- **TEEF-SIG-14** When later verification is required, the recipient SHOULD archive the exact manifest bytes, the attachments, and the relevant trust material.

*Note:* A JWS created by the publisher attests to what the publisher released. It does not vouch for third-party artefacts. The recipient remains responsible for evaluating issuers, scope, freshness, and sufficiency.

[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation), [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339), [JWS](https://www.rfc-editor.org/rfc/rfc7515), [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161)

## Rule index

`Role` names who the rule binds. `Tested` is `yes` when the [conformance suite](../conformance/README.md) has cases for the rule, `schema` when the JSON Schema enforces it and cases report TEEF-SCHEMA-01, and `no` when a package cannot show whether the rule was followed.

| ID | Rule | Role | Tested |
|---|---|---|---|
| TEEF-PKG-01 | Reject a package that breaks a content requirement | recipient | no |
| TEEF-PKG-02 | Manifest is UTF-8 JSON without a byte order mark | both | yes |
| TEEF-PKG-03 | Manifest has no duplicate member names | both | yes |
| TEEF-PKG-04 | A single-file package is a ZIP with the manifest at its root | both | yes |
| TEEF-PKG-05 | ZIP entries use the manifest's relative paths | both | no |
| TEEF-PKG-06 | `generatedAt` is RFC 3339 UTC with `Z` | both | schema |
| TEEF-PKG-07 | A package contains questionnaires, evidence, or both | both | schema |
| TEEF-SIG-01 | Assemble the ZIP before encryption | publisher | no |
| TEEF-SIG-02 | Encrypt as a compact JWE for one recipient | publisher | no |
| TEEF-SIG-03 | JWE protected header values | both | no |
| TEEF-SIG-04 | Decrypt and authenticate before opening the ZIP | recipient | no |
| TEEF-SIG-05 | Validate the decrypted package | recipient | no |
| TEEF-SCHEMA-01 | Validate the manifest against the schema with format assertions | recipient | yes |
| TEEF-SCHEMA-02 | Report an unsupported schema version | recipient | yes |
| TEEF-ID-01 | Assign a new package ID per snapshot and never reuse it | publisher | no |
| TEEF-ID-02 | Treat a reused package ID as an integrity error | recipient | yes |
| TEEF-REF-01 | `supersedes` names an earlier package of the same publisher and subject | publisher | no |
| TEEF-SCOPE-01 | Supply the service for service-specific exchanges | publisher | no |
| TEEF-ANS-01 | Use the buyer's questionnaire URI | publisher | no |
| TEEF-ANS-02 | Do not read an omitted question as a status | recipient | no |
| TEEF-SCOPE-02 | A subject scope has at least one field | both | schema |
| TEEF-SCOPE-03 | List every country of operation, support, or processing | publisher | no |
| TEEF-SCOPE-04 | Check the subject scope against own knowledge | recipient | no |
| TEEF-SCOPE-05 | Do not treat the subject scope as verified | recipient | no |
| TEEF-SCOPE-06 | Surface a subject organisation the evidence does not cover | recipient | yes |
| TEEF-SCOPE-07 | Compare organisations by identifier | recipient | no |
| TEEF-SCOPE-08 | Show both names when an identifier is missing | recipient | yes |
| TEEF-SCOPE-09 | Surface subject countries the evidence does not list | recipient | yes |
| TEEF-ANS-03 | `answered` carries an answer | both | schema |
| TEEF-ANS-04 | `reference` carries evidence references | both | schema |
| TEEF-ANS-05 | `reference` carries no answer | both | schema |
| TEEF-ANS-06 | `unknown`, `notApplicable`, and `withheld` carry no answer or references | both | schema |
| TEEF-ANS-07 | Preserve `false` and `0` | both | no |
| TEEF-ANS-08 | Match questionnaire URI, version, and question ID before applying | recipient | no |
| TEEF-ANS-09 | Interpret choice codes and units with the definition | recipient | no |
| TEEF-ANS-10 | Reproduce the question text as received | publisher | no |
| TEEF-MAP-01 | Do not assume an unqualified mapping is equivalent | recipient | no |
| TEEF-MAP-02 | Reuse mapped answers only with review or policy for equivalent mappings | recipient | no |
| TEEF-EV-01 | File digests are lowercase hex SHA-256 of the exact bytes | both | schema |
| TEEF-URI-01 | External references use HTTPS | both | schema |
| TEEF-URI-02 | External URIs carry no credentials | both | schema |
| TEEF-EV-02 | Do not assume an undigested external target is unchanged | recipient | no |
| TEEF-EV-03 | Supply issuer and scope where known | publisher | no |
| TEEF-EV-04 | Do not infer omitted metadata | recipient | no |
| TEEF-EV-05 | Follow the metadata guidance per kind | publisher | no |
| TEEF-REF-02 | A bridge letter references a bridged report in the package | publisher | no |
| TEEF-EV-06 | A bridge letter names a bridged report outside the package | publisher | no |
| TEEF-EV-07 | An insurance certificate's scope states the cover type | publisher | no |
| TEEF-EV-08 | Prefer a specific kind over `other` | publisher | no |
| TEEF-EV-09 | An `other` item's title describes it | publisher | no |
| TEEF-REF-03 | `bridges` appears only on a bridge letter | both | yes |
| TEEF-REF-04 | `bridges` references an assurance report | both | yes |
| TEEF-REF-05 | No self-reference in related evidence | both | yes |
| TEEF-DATE-01 | A bridge letter's coverage starts the day after the report's | publisher | no |
| TEEF-DATE-02 | Surface a bridge letter gap or overlap | recipient | yes |
| TEEF-AR-01 | Only assurance reports carry assurance report details | both | schema |
| TEEF-AR-02 | A type 1 report covers a single date | both | yes |
| TEEF-AR-03 | A type 2 report covers more than one date | both | yes |
| TEEF-AR-04 | Copy report details without reinterpretation | publisher | no |
| TEEF-AR-05 | Report organisations and countries stay within the system boundary | publisher | no |
| TEEF-AR-06 | Do not list countries of carved-out subservice organisations only | publisher | no |
| TEEF-AR-07 | Surface an opinion other than unmodified | recipient | yes |
| TEEF-AR-08 | Surface reported exceptions | recipient | yes |
| TEEF-AR-09 | Surface carved-out subservice organisations | recipient | yes |
| TEEF-AR-10 | Surface complementary user entity controls | recipient | yes |
| TEEF-AR-11 | Encrypt or omit confidential report details | publisher | no |
| TEEF-CERT-01 | A certificate carries certificate details | both | schema |
| TEEF-CERT-02 | Only certificates carry certificate details | both | schema |
| TEEF-CERT-03 | A certificate has no common `scope` | both | schema |
| TEEF-CERT-04 | A Statement of Applicability has a version or date | both | schema |
| TEEF-CERT-05 | Copy certificate details without reinterpretation | publisher | no |
| TEEF-CERT-06 | Supply the certificate number when one exists | publisher | no |
| TEEF-CERT-07 | Surface a certificate without a number | recipient | yes |
| TEEF-CERT-08 | Certificate organisations and countries stay within the certified scope | publisher | no |
| TEEF-CERT-09 | Surface a certificate without an accreditation body | recipient | yes |
| TEEF-CERT-10 | Surface a last audit more than 12 months old | recipient | yes |
| TEEF-CERT-11 | Check the certificate register where policy allows | recipient | no |
| TEEF-ID-03 | Reject duplicate identifiers and file paths | recipient | yes |
| TEEF-REF-06 | Reject unresolved evidence references | recipient | yes |
| TEEF-REF-07 | Reject a package that supersedes itself | recipient | yes |
| TEEF-REF-08 | Reject a superseded package with a different publisher or subject | recipient | yes |
| TEEF-DATE-03 | Reject inverted validity or coverage ranges | recipient | yes |
| TEEF-DATE-04 | Do not reject solely for expiry or missing scope | recipient | no |
| TEEF-DATE-05 | Surface evidence expired at generation or at intake | recipient | yes |
| TEEF-EV-10 | Surface evidence without a stated scope | recipient | yes |
| TEEF-ANS-11 | Check answer types against the definition | recipient | no |
| TEEF-ANS-12 | Surface an unknown questionnaire or version | recipient | yes |
| TEEF-ANS-13 | Do not apply answers to an unknown questionnaire automatically | recipient | no |
| TEEF-ANS-14 | Surface question text that differs from the definition | recipient | no |
| TEEF-EV-11 | Reject missing files and digest mismatches | recipient | yes |
| TEEF-ARC-01 | Reject undeclared files | recipient | yes |
| TEEF-ARC-02 | Reject absolute paths and path traversal | recipient | yes |
| TEEF-ARC-03 | Reject reserved device filenames | recipient | yes |
| TEEF-ARC-04 | Reject symbolic and hard links | recipient | yes |
| TEEF-ARC-05 | Reject duplicate entries | recipient | yes |
| TEEF-ARC-06 | Reject case-insensitive collisions | recipient | yes |
| TEEF-ARC-07 | Enforce archive size, entry count, and expanded size limits | recipient | yes |
| TEEF-ARC-08 | Apply file inspection policy | recipient | no |
| TEEF-URI-03 | Treat package content as untrusted | recipient | no |
| TEEF-URI-04 | Do not dereference external references during validation | recipient | no |
| TEEF-URI-05 | Follow network policy for later retrieval | recipient | no |
| TEEF-URI-06 | Flag external URIs that appear to carry credentials | recipient | yes |
| TEEF-DIST-01 | Disclose only permitted material | publisher | no |
| TEEF-DIST-02 | Use access-controlled references for restricted material | publisher | no |
| TEEF-DIST-03 | Apply distribution and retention policy | recipient | no |
| TEEF-DIST-04 | Retain the snapshot and verification result | recipient | no |
| TEEF-SIG-06 | Detached JWS over the exact manifest bytes | both | no |
| TEEF-SIG-07 | JWS header values | both | no |
| TEEF-SIG-08 | Resolve the signing key through trusted configuration | recipient | no |
| TEEF-SIG-09 | RFC 3161 token over the exact manifest bytes | both | no |
| TEEF-SIG-10 | Verify the timestamp token | recipient | no |
| TEEF-SIG-11 | Separate signing and encryption keys | both | no |
| TEEF-SIG-12 | Reject invalid proofs | recipient | no |
| TEEF-SIG-13 | Reject a package missing a required proof | recipient | no |
| TEEF-SIG-14 | Archive material for later verification | recipient | no |
