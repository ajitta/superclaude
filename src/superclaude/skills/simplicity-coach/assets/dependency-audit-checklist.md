<component name="dependency-audit-checklist" type="reference" parent="simplicity-coach">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <meta>Referenced from SKILL.md as `assets/dependency-audit-checklist.md`</meta>

  <pre_add_checklist title="Before Adding a New Dependency">
    <required_questions>
| # | Question | Answer |
|---|----------|--------|
| 1 | How many lines of this library's features do we actually use? | |
| 2 | How long would it take to write those lines ourselves? | |
| 3 | Are we confident this dependency will remain safe and compatible in 6 months? | |
    </required_questions>

    <justification note="At least one must be met">
- [ ] Domain requiring specialized knowledge (cryptography, compression, media processing)
- [ ] Would require hundreds of lines + many edge cases to implement ourselves
- [ ] Library is mature with active maintenance (release within last 6 months)
- [ ] Using the library's core functionality (not a peripheral utility)
- [ ] Security vulnerability patches handled promptly
    </justification>

    <warning_signs note="Reconsider if any apply">
- [ ] Using less than 10% of library functionality
- [ ] No releases in the past year
- [ ] Only 1 maintainer
- [ ] 50+ transitive dependencies
- [ ] "Everyone uses it" is the only reason
- [ ] Functionality replaceable with native APIs
    </warning_signs>
  </pre_add_checklist>

  <regular_audit title="Existing Dependencies — Quarterly Review">
    <step n="1" title="Identify Unused">
- `npx depcheck` (Node.js)
- `pip-autoremove --list` (Python)
- `bundle clean --dry-run` (Ruby)
    </step>
    <step n="2" title="Check Vulnerabilities">
- `npm audit` / `yarn audit`
- `pip-audit`
- `bundle audit`
    </step>
    <step n="3" title="Evaluate Replaceability">
- Can it be replaced with native APIs?
- Is there a lighter alternative?
- Can we extract only the features we use (tree-shaking)?
    </step>

    <osl_removal title="Orient-Step-Learn for Dependency Removal">
1. **Orient**: Understand what the dependency does, where it's used, how to replace it
2. **Step**: Remove only one dependency and run tests
3. **Learn**: Build pass? Runtime errors? Performance changes?
    </osl_removal>
  </regular_audit>

  <hidden_costs title="The Time Bomb — Dave Thomas">
- **Supply Chain Attack**: Sept 2025 npm incident — 18 packages including chalk, debug compromised
- **Breaking Change**: API changes during major version updates
- **Dependency Hell**: A requires B@1.x while C requires B@2.x
- **Abandoned Maintenance**: Maintainer abandons the project
- **License Change**: Open source → commercial (Redis, Elasticsearch cases)
- **Performance Debt**: Unused code increases bundle size and build time

"Is it worth taking on these risks just to save 3 lines?" — the key question.
  </hidden_costs>
</component>
