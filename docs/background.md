# Background and rationale for TEEF

The TPRM Evidence Exchange Format (TEEF) gives suppliers and recipients a common, machine-readable way to exchange questionnaire responses and evidence for third-party risk management (TPRM). A supplier can generate a package from the systems it already uses. A buyer or assessor can read that package and import it into its existing review workflow.

## Why the exchange needs a common format

During onboarding and renewals, a buyer may ask a supplier for answers, a certificate, a subprocessor list, and a restricted assurance report. The supplier might keep those items in a questionnaire database, a trust centre, a document repository, and a spreadsheet. When the items arrive through separate channels, the reviewer has to match each document to the relevant answer, check its scope, and record what was reviewed.

Those details matter. A valid certificate may cover a different legal entity or service. A live subprocessor page may change after the review. A questionnaire answer may only make sense for the version of the question the supplier received. An evidence exchange should carry enough context for a recipient to identify what was provided and decide whether it applies.

## How TEEF helps

- **Reuse existing sources.** A supplier can assemble a package from spreadsheets, TPRM tools, trust centres, or questionnaire databases. The supplier owns its adapters and decides what material is approved for release.
- **Reduce manual intake.** A versioned JSON manifest identifies the supplier, the assessed subject, and the questionnaire and question IDs. It distinguishes direct answers, references that supply an answer, and evidence that supports a response. Files keep their original format.
- **Reuse answers across questionnaires.** Buyers keep their own questionnaires, and TEEF does not impose a control taxonomy. A response can map to equivalent or overlapping questions in other buyers' questionnaires, control frameworks, or the supplier's answer library, and states whether the match is exact, broader, narrower, or partial. A recipient can recognise an answer it has already reviewed, and only exact matches qualify for reuse without a reviewer. A response can also carry the question text as asked, so a recipient can detect a question that changed without a new version.
- **Make evidence reviewable, not just attached.** Evidence kinds cover the artefacts commonly exchanged, including assurance reports, bridge letters, penetration tests, continuity tests, policies, insurance certificates, agreements, and architecture diagrams. An assurance report can state its standard, type, opinion, exceptions, carved-out subservice organisations, and the controls the customer is expected to operate. A certificate states its standard and certified scope, and can carry its number, accreditation body, last audit, and a link to the certification body's register. A bridge letter can point to the report it extends, so a reviewer can check that the coverage periods join up.
- **Compare scope.** The subject can describe where the service operates and which components it includes. Certificates and assurance reports can list the legal entities and countries they cover. A recipient can then flag an entity or country the evidence does not cover, which is the gap that is easiest to miss in manual review. The certificate or report wording stays authoritative, and the subject scope remains the supplier's own statement for the recipient to check.
- **Preserve a review snapshot.** A package ID and attachment hashes help the recipient identify what arrived and detect changed files. Optional signing and trusted timestamps support later verification. Whole-package encryption protects the manifest and attachments when the exchange contains confidential material. [Package structure and security bindings](architecture.md)

The exchange can also carry evidence on its own. For example, a supplier can send a new subprocessor list during a renewal. The buyer can associate it with the covered service and retain the earlier snapshot where its evidence policy requires it.

## Where TEEF fits

TEEF defines the package that crosses the organisational boundary. Each party can choose its own collection, transfer, and intake tooling. Structured assessment material can travel alongside a PDF or a text file. For example, a supplier that already produces an OSCAL assessment document can include it as evidence. The recipient remains responsible for assessing scope, freshness, and sufficiency. [NIST OSCAL layers and models](https://pages.nist.gov/OSCAL/learn/concepts/layer/)

The practical test is a real onboarding or renewal. A supplier generates the package from an existing source and the buyer uses it to replace a request or an intake step. Fewer follow-ups, less manual re-entry, and a traceable record of the evidence reviewed are the outcomes TEEF is meant to support.

To see what the format carries, start with the [example package](examples/supplier-package/manifest.json).
