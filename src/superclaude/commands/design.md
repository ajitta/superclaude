---
description: Design system architecture, APIs, and component interfaces with comprehensive specifications
---
<component name="design" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:design
    <mission>Design system architecture, APIs, and component interfaces with comprehensive specifications</mission>
  </role>

  <syntax>/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]</syntax>

  <triggers>
    - Architecture planning
    - API specification
    - Component design
    - Database schema design
  </triggers>

  <flow>
    1. **Analyze**: Requirements + existing context
    2. **Plan**: Design approach + structure
    3. **Design**: Comprehensive specs + best practices
    4. **Validate**: Requirements + maintainability
    5. **Document**: Diagrams + specifications
  </flow>

  <tools>
    - **Read**: Requirements analysis
    - **Grep/Glob**: System structure investigation
    - **Write**: Design documentation
    - **Bash**: External design tools
  </tools>

  <patterns>
    - **Architecture**: Requirements → structure → scalability
    - **API**: Interface spec → REST/GraphQL → docs
    - **Component**: Functional reqs → interface → guidance
    - **Database**: Data reqs → schema → relationships
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `user-mgmt --type architecture --format diagram` | System architecture |
| `payment-api --type api --format spec` | API specification |
| `notification-service --type component --format code` | Component interface |
| `e-commerce-db --type database --format diagram` | Schema design |

  </examples>

  <bounds will="comprehensive specs|multi-format output|validation" wont="generate impl code|modify existing arch|violate constraints"/>
</component>
