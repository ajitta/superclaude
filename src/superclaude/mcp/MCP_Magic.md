<component name="magic" type="mcp">
  <role>
    <mission>Modern UI component generation from 21st.dev patterns with design system integration</mission>
  </role>

  ## Activation
  Not always active. When UI component generation is needed:
  1. `mcp-find("magic")` or `mcp-find("21st")` — locate in MCP Docker catalog
  2. `mcp-add("magic")` — activate for current session
  3. Components generated follow 21st.dev design patterns

  <choose>
  Use:
  - Production UI components: forms, navbars, cards, modals, tables
  - Accessible by default: ARIA roles, keyboard navigation, focus management
  - Design system consistency: tokens, spacing, typography from existing system
  - Modern frameworks: React, Vue, Angular — idiomatic component patterns
  - Responsive: mobile-first, breakpoint-aware layouts

  Avoid:
  - Backend logic: API endpoints, database queries, server config → native Claude
  - Business logic: validation rules, state machines → native Claude
  - Styling only: CSS tweaks, theme changes → Edit tool
  - Data fetching: API integration, caching → native Claude
  </choose>

  ## Component Request Patterns
  - **Specify framework**: "React login form" not just "login form"
  - **State accessibility**: "with keyboard navigation and screen reader support"
  - **Design tokens**: reference existing design system when available
  - **Responsive requirements**: specify breakpoints if non-standard

  ## Quality Defaults
  Magic components include by default:
  - Semantic HTML elements
  - ARIA attributes for screen readers
  - Keyboard interaction (Tab, Enter, Escape)
  - Focus management and visible focus indicators
  - Responsive breakpoints (mobile, tablet, desktop)

  ## Integration Patterns
  - **New component**: Magic:generate → /sc:implement:integrate → /sc:test --type e2e
  - **Design system**: Magic:component → adapt to existing tokens → /sc:review --focus a11y
  - **Prototype**: Magic:rapid-generate → Playwright:visual-check → iterate
  - **A11y-first**: Magic:accessible-component → Playwright:axe-audit → /sc:analyze --focus a11y

  <examples>
| Input | Action | Reason |
|-------|--------|--------|
| create React login form | Magic: generate with a11y, validation states, responsive | Production UI component |
| responsive data table with sorting | Magic: sortable table, mobile-friendly, keyboard nav | Complex UI pattern |
| add dark mode toggle | Magic: toggle component with prefers-color-scheme | Design system component |
| write REST API endpoint | Native Claude | Backend logic, not UI |
  </examples>

  <bounds will="UI component generation|design system integration|accessible components|responsive layouts" wont="backend logic|API design|database operations|business logic" fallback="Use native Claude for non-UI code, Context7 for framework-specific patterns"/>

  <handoff next="/sc:implement /sc:design --type component /sc:analyze --focus a11y"/>
</component>
