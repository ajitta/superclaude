<component name="dependency-audit-checklist" type="reference" parent="simplicity-coach">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <meta>Referenced from SKILL.md as `assets/dependency-audit-checklist.md`</meta>

  <pre_add title="Before Adding a New Dependency">
Required questions:
| # | Question |
|---|----------|
| 1 | How many lines of this library do we actually use? |
| 2 | How long to write those lines ourselves? |
| 3 | Confident it stays safe and compatible in 6 months? |

Justification (at least one):
- [ ] Specialized domain (crypto, compression, media)
- [ ] Hundreds of lines + many edge cases to DIY
- [ ] Mature, actively maintained (release within 6 months)
- [ ] Using core functionality, not peripheral utility
- [ ] Security patches handled promptly

Warning signs (reconsider if any):
- [ ] Using &lt;10% of library functionality
- [ ] No releases in past year
- [ ] Single maintainer
- [ ] 50+ transitive dependencies
- [ ] "Everyone uses it" as only reason
- [ ] Replaceable with native APIs
  </pre_add>

  <regular_audit title="Quarterly Review">
1. Identify unused: `npx depcheck` | `pip-autoremove --list` | `bundle clean --dry-run`
2. Check vulnerabilities: `npm audit` | `pip-audit` | `bundle audit`
3. Evaluate replaceability: native API? lighter alternative? tree-shaking?

OSL for removal: Orient (what it does, where used, how to replace) → Step (remove one, run tests) → Learn (build pass? runtime errors? perf change?)
  </regular_audit>

  <hidden_costs title="The Time Bomb — Dave Thomas">
- Supply Chain Attack: Sept 2025 npm — 18 packages compromised
- Breaking Change: API changes on major version updates
- Dependency Hell: A requires B@1.x, C requires B@2.x
- Abandoned Maintenance: maintainer walks away
- License Change: open source → commercial (Redis, Elasticsearch)
- Performance Debt: unused code inflates bundle and build time

"Is it worth these risks just to save 3 lines?"
  </hidden_costs>
</component>
