# Gates by stack — the lightest tool per property

Contents: Java · Kotlin · Python · TypeScript/JavaScript · Go · C# · Rust · Sonar

For each stack: dependency direction, length and complexity, duplication. One tool per property, the minimal config, the command. Prefer what the repo already
has; add only what covers a property nothing covers yet. Tools install through the repo's dev-dependency group; jscpd needs Node and is the fallback where a
stack has no native duplication check.

## Java (Maven or Gradle)

| Property | Tool | Config | Command |
|---|---|---|---|
| Dependency direction, cycles, layers | ArchUnit (a test) | a `*ArchitectureTest` with `layeredArchitecture()` and `slices().should().beFreeOfCycles()`; existing tests stay as they are | the test suite, or `mvn -Dtest=*ArchitectureTest test` |
| Length and complexity | Checkstyle (`MethodLength` 40, `CyclomaticComplexity` 10) or PMD (`ExcessiveMethodLength`, `CyclomaticComplexity`, `GodClass`) | `checkstyle.xml` / `pmd-ruleset.xml` wired into the build plugin | `mvn checkstyle:check` / `mvn pmd:check` |
| Duplication | PMD CPD | `minimumTokens` ≈ 100 | `mvn pmd:cpd-check` |

## Kotlin

| Property | Tool | Config | Command |
|---|---|---|---|
| Dependency direction | Konsist (a test) or ArchUnit | a test asserting package dependencies | the test suite |
| Length and complexity | detekt (`LongMethod` threshold 40, `CyclomaticComplexMethod` 10) | `detekt.yml` | `./gradlew detekt` |
| Duplication | detekt is limited; PMD CPD supports Kotlin | CPD with `--language kotlin` | `pmd cpd --minimum-tokens 100 --language kotlin --dir src` |

## Python

| Property | Tool | Config | Command |
|---|---|---|---|
| Dependency direction, layers | import-linter | `[tool.importlinter]` in `pyproject.toml` with a `layers` contract | `lint-imports` |
| Length and complexity | ruff — `C901` complexity 10, `PLR0915` statements 40 (no Python linter counts lines per function; statements are the proxy, and the map says so) | `[tool.ruff.lint] select = ["C901", "PLR0915"]`, `mccabe.max-complexity = 10`, `pylint.max-statements = 40` | `ruff check <files>` |
| Duplication | pylint `duplicate-code` (R0801) — native; jscpd if Node is already present | `[tool.pylint.similarities] min-similarity-lines = 10` | `pylint --disable=all --enable=duplicate-code <package>` |

## TypeScript / JavaScript

| Property | Tool | Config | Command |
|---|---|---|---|
| Dependency direction, cycles | dependency-cruiser | `.dependency-cruiser.cjs` with `forbidden` rules (no cycles, layer direction) | `depcruise src --config` |
| Length and complexity | eslint (`complexity: [error, 10]`, `max-lines-per-function: [error, 40]`, `max-depth`) | in the eslint config | `eslint <files>` |
| Duplication | jscpd | `.jscpd.json`, `minLines: 10` | `jscpd src` |

## Go

| Property | Tool | Config | Command |
|---|---|---|---|
| Dependency direction | golangci-lint `depguard`, or go-arch-lint | `.golangci.yml` depguard rules / `.go-arch-lint.yml` | `golangci-lint run` |
| Length and complexity | golangci-lint `funlen` (40 lines), `gocyclo` (10), `gocognit` | `.golangci.yml` | `golangci-lint run <packages>` |
| Duplication | golangci-lint `dupl` | `dupl.threshold: 100` tokens | `golangci-lint run` |

## C#

| Property | Tool | Config | Command |
|---|---|---|---|
| Dependency direction | ArchUnitNET (a test) | a test with `Types().That().ResideInNamespace(...)` rules | `dotnet test` |
| Length and complexity | Roslyn analyzers (`CA1502` complexity) and `.editorconfig` severity | `.editorconfig` | `dotnet build -warnaserror` |
| Duplication | jscpd | `.jscpd.json` | `jscpd src` |

## Rust

| Property | Tool | Config | Command |
|---|---|---|---|
| Dependency direction | cargo-modules (report) or a workspace layout that makes wrong dependencies impossible | crate boundaries | `cargo modules dependencies` |
| Length and complexity | clippy (`cognitive_complexity` threshold 10, `too_many_lines` 40) | `clippy.toml` | `cargo clippy -- -D warnings` |
| Duplication | jscpd | `.jscpd.json` | `jscpd src` |

## Sonar

SonarQube or SonarCloud covers all three properties but needs a server or an account. Use it only when the repo already runs it: record its command and the
quality gate it enforces in the map. Never propose it as a first gate.
