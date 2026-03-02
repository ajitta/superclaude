<component name="playwright" type="mcp">
  <role>
    <mission>Browser automation and E2E testing with real browser interaction</mission>
  </role>

  <choose>
Use:
- Real browser: Actual rendering, not just code
- Integration testing: User journeys, visual validation over unit tests
- E2E: Login flows, form submissions, multi-page workflows
- Visual testing: Screenshots, responsive design validation

Avoid:
- Code analysis: Static review, syntax, logic validation
  </choose>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| test login flow | Playwright | browser automation |
| form validation works | Playwright | real user interaction |
| screenshots responsive design | Playwright | visual testing |
| accessibility compliance | Playwright | automated WCAG |
| review function logic | Native Claude | static analysis |
  </examples>

  <workflows>
    <e2e_test>
1. browser_navigate to target URL
2. browser_click, browser_type to simulate user journey
3. browser_snapshot to verify DOM state after each step
4. browser_take_screenshot for visual evidence
5. browser_close when test sequence completes
    </e2e_test>
    <visual_regression>
1. Navigate to page at defined viewport → browser_take_screenshot as baseline
2. Apply code changes → browser_take_screenshot as comparison
3. Compare for unintended drift; repeat at 375px, 768px, 1280px
    </visual_regression>
  </workflows>

  <scenarios>
    <form_interaction>
Scenario: validate multi-step checkout form
1. browser_navigate /checkout → browser_type shipping fields
2. browser_click "Continue to Payment" → browser_snapshot verify step
3. browser_type card fields → browser_click "Place Order"
4. browser_snapshot: verify confirmation page and order ID
    </form_interaction>
    <responsive_validation>
Scenario: verify navbar collapses to hamburger on mobile
1. browser_resize 375x812 → browser_snapshot: hamburger visible, links hidden
2. browser_click hamburger → browser_snapshot: overlay open
3. browser_resize 1280x800 → browser_snapshot: horizontal nav restored
    </responsive_validation>
  </scenarios>

  <tool_guide>
- Prefer browser_snapshot over screenshot for DOM assertions (faster, text-based)
- Use browser_take_screenshot only when visual evidence is needed
- Chain browser_click → browser_snapshot for step-by-step validation
- Combine with --devtools for performance-aware E2E testing
  </tool_guide>
</component>
