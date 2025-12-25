<component name="context7" type="mcp">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>library|docs|framework|documentation|import|require</triggers>

  <role>
    <mission>Official library documentation lookup and framework pattern guidance</mission>
  </role>

  <choose>
    <use context="curated docs">Version-specific documentation over WebSearch</use>
    <use context="official patterns">Implementation must follow official patterns</use>
    <use context="frameworks">React hooks, Vue composition API, Angular services</use>
    <use context="libraries">Correct API usage, auth flows, configuration</use>
    <use context="compliance">Adherence to official standards</use>
  </choose>

  <synergy>
    <with n="Sequential">Context7 provides docs → Sequential analyzes strategy</with>
    <with n="Magic">Context7 supplies patterns → Magic generates components</with>
  </synergy>

  <examples>
    <ex i="implement React useEffect" o="Context7" r="official React patterns"/>
    <ex i="add Auth0 authentication" o="Context7" r="official Auth0 docs"/>
    <ex i="migrate to Vue 3" o="Context7" r="official migration guide"/>
    <ex i="just explain this function" o="Native Claude" r="no external docs needed"/>
  </examples>
</component>
