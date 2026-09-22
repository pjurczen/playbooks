# Gates by stack — the lightest tool per property

Contents: Java · Kotlin · Python · TypeScript/JavaScript · Go · C# · Rust · Sonar

For each stack: dependency direction, length and complexity, duplication. One tool per property, the minimal config, the command. Prefer what the repo already has; add only what covers a property nothing covers yet.

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
| Length and complexity | ruff (`C901` max-complexity 10, `PLR0915` statements) plus xenon for a hard ceiling | `[tool.ruff.lint] select = ["C901"]`, `mccabe.max-complexity = 10` | `ruff check <files>`; `xenon --max-absolute B <files>` |
| Duplication | jscpd (any language) | `.jscpd.json` with `minLines: 10` | `jscpd <paths>` |

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

SonarQube or SonarCloud covers all three properties but needs a server or an account. Use it only when the repo already runs it: record its command and the quality gate it enforces in the map. Never propose it as a first gate.
