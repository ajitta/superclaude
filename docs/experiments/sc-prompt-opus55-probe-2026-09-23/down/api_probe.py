"""Run the EN rewrite and the EN original on claude-opus-5-5 via the Messages API."""

import json
import pathlib
import time

import anthropic

D = pathlib.Path(__file__).parent
client = anthropic.Anthropic()
for name in ("en-new", "en-base"):
    prompt = (D / name / "prompt.txt").read_text()
    t = time.time()
    with client.messages.stream(
        model="claude-opus-5-5",
        max_tokens=128000,
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": "medium"},
        messages=[{"role": "user", "content": prompt}],
    ) as s:
        msg = s.get_final_message()
    text = "".join(b.text for b in msg.content if b.type == "text")
    thinking = "".join(
        getattr(b, "thinking", "") for b in msg.content if b.type == "thinking"
    )
    (D / name / "api_out.txt").write_text(text)
    (D / name / "api_thinking.txt").write_text(thinking)
    print(
        json.dumps(
            {
                "run": name,
                "stop_reason": msg.stop_reason,
                "usage": msg.usage.model_dump(),
                "secs": round(time.time() - t, 1),
                "text_chars": len(text),
                "thinking_chars": len(thinking),
            }
        )
    )
