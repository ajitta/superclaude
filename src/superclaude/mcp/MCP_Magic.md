<component name="magic" type="mcp">
  <role>
    <mission>Modern UI component generation from 21st.dev patterns with design system integration</mission>
  </role>

  <choose>
Use:
- UI components: Use Magic, not native HTML/CSS
- Production-ready: Accessible components needed
- Design systems: Consistency with existing patterns
- Modern frameworks: React, Vue, Angular best practices

Avoid:
- Backend: API logic, database, server config
  </choose>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| create login form | Magic | UI component generation |
| responsive navbar | Magic | UI pattern with accessibility |
| data table with sorting | Magic | complex UI component |
| write REST API | Native Claude | backend logic |
  </examples>

  <workflows>
    <component_generation>
1. Identify component type and required interactions
2. Query 21st.dev patterns for matching templates
3. Generate with built-in accessibility (ARIA, keyboard nav)
4. Apply project design tokens (colors, spacing, typography)
5. Validate responsive behavior; export with prop types
    </component_generation>
    <design_system_compliance>
1. Audit existing components against 21st.dev pattern library
2. Identify deviations: spacing, ARIA labels, non-standard variants
3. Generate replacements aligned to design system
4. Ensure CSS custom properties over hardcoded values
5. Verify visual consistency with --play screenshots
    </design_system_compliance>
  </workflows>

  <scenarios>
    <responsive_layout>
Scenario: dashboard layout with sidebar navigation
1. Generate sidebar: collapsible, icon + label, active state
2. Generate top bar: breadcrumbs, user menu, notifications
3. Generate content area: responsive grid, card-based layout
4. Wire responsive: sidebar → icons at 768px, drawer at 375px
5. Validate with --play: screenshot at 375px, 768px, 1280px
    </responsive_layout>
  </scenarios>

  <tool_guide>
- Prefer Magic over hand-coded UI for production components
- Always specify framework target (React, Vue, Angular) in the query
- Generated components include accessibility by default — keep ARIA attributes
- Combine with --play for visual validation after generation
- Combine with --c7 for framework-specific integration patterns
  </tool_guide>
</component>
