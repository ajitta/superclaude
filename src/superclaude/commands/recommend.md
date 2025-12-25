<component name="recommend" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:recommend
    <mission>Ultra-intelligent command recommendation engine for optimal SuperClaude command selection</mission>
  </role>

  <syntax>/sc:recommend [request] [--estimate] [--alternatives] [--stream] [--expertise beginner|intermediate|expert]</syntax>

  <triggers>
    <t>Command recommendation requests</t>
    <t>Help choosing approach</t>
    <t>Project planning assistance</t>
  </triggers>

  <flow>
    <s n="1">Analyze: User request + project context</s>
    <s n="2">Classify: Category + expertise level</s>
    <s n="3">Map: Keywords → commands + personas</s>
    <s n="4">Recommend: Flow + MCP + flags</s>
  </flow>

  <keyword_map>
    <cat n="ml" kw="machine learning|ml|ai|model" cmd="/sc:analyze --seq --c7|/sc:design --seq --ultrathink"/>
    <cat n="web" kw="website|frontend|ui|react|vue" cmd="/sc:build --feature --magic|/sc:test --e2e --pup"/>
    <cat n="api" kw="api|backend|server|microservice" cmd="/sc:design --api --ddd --seq|/sc:build --feature --tdd"/>
    <cat n="debug" kw="error|bug|issue|not working" cmd="/sc:troubleshoot --investigate --seq|/sc:analyze --code"/>
    <cat n="perf" kw="slow|performance|optimization" cmd="/sc:analyze --performance --pup --profile|/sc:improve --performance"/>
    <cat n="sec" kw="security|auth|vulnerability|owasp" cmd="/sc:scan --security --owasp --deps|/sc:analyze --security"/>
    <cat n="test" kw="test|qa|coverage|e2e" cmd="/sc:test --coverage --e2e --pup|/sc:scan --validate"/>
    <cat n="learn" kw="how|learn|explain|tutorial" cmd="/sc:document --user --examples|/sc:brainstorm --interactive"/>
  </keyword_map>

  <project_detect>
    <proj n="react" ind="package.json+react|src/App.jsx" flags="--magic --c7 --pup"/>
    <proj n="node_api" ind="express|server.js|routes/" flags="--seq --c7"/>
    <proj n="python" ind="requirements.txt|setup.py|main.py" flags="--seq"/>
  </project_detect>

  <expertise_flags>
    <level n="beginner">--tutorial --examples --step-by-step</level>
    <level n="intermediate">--guided --examples</level>
    <level n="expert">--advanced --no-explanations</level>
  </expertise_flags>

  <examples>
    <ex i="'I want to do machine learning'" o="🎯ML-Beginner → analyze+design flow"/>
    <ex i="'my site is very slow'" o="🎯Perf-Urgent → analyze+troubleshoot+improve"/>
    <ex i="'building e-commerce' --estimate" o="🎯Multi-domain → design+build+scan + timeline"/>
  </examples>

  <bounds will="intelligent mapping|project context|expertise adaptation" wont="execute commands|make assumptions without context"/>
</component>
