---
id: downsides
name: Downsides written down
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: pass
batch: 1
sources:
  - Nygard 2011 (all consequences should be listed, not just the positive ones)
  - Rust RFC template (Drawbacks section)
  - Kubernetes KEP template (Risks and Mitigations)
---

Decide whether the document names at least one cost, risk or thing that gets worse under the chosen approach.

Pass when the document states something the approach makes worse, harder, slower, riskier or more expensive, or something that stops working, or a way the
approach could fail in practice.

Fail when every consequence listed is a benefit, when the only "downside" is that unrelated things stay unchanged, or when risks are mentioned only for the
alternatives that were rejected.

Unknown when a stated consequence could be read either way.

Evidence: for a pass, quote the downside. A fail needs no quote.
