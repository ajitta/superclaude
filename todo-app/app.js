(function () {
  "use strict";

  let todos = Storage.load();
  let filter = "all";

  const form = document.getElementById("todo-form");
  const input = document.getElementById("todo-input");
  const list = document.getElementById("todo-list");
  const empty = document.getElementById("empty");
  const status = document.getElementById("status");
  const filtersEl = document.getElementById("filters");

  function uid() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  function visible() {
    if (filter === "active") return todos.filter(t => !t.done);
    if (filter === "done") return todos.filter(t => t.done);
    return todos;
  }

  function render() {
    const items = visible();
    list.replaceChildren();

    items.forEach(todo => {
      const li = document.createElement("li");
      if (todo.done) li.classList.add("done");
      li.dataset.id = todo.id;

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = todo.done;
      checkbox.setAttribute("aria-label", `${todo.text} 완료 여부`);
      checkbox.addEventListener("change", () => toggle(todo.id));

      const text = document.createElement("span");
      text.className = "text";
      text.textContent = todo.text;

      const del = document.createElement("button");
      del.type = "button";
      del.className = "delete";
      del.textContent = "삭제";
      del.setAttribute("aria-label", `${todo.text} 삭제`);
      del.addEventListener("click", () => remove(todo.id));

      li.append(checkbox, text, del);
      list.appendChild(li);
    });

    empty.hidden = items.length > 0;

    const total = todos.length;
    const open = todos.filter(t => !t.done).length;
    status.textContent = total === 0 ? "" : `남은 일 ${open} / 전체 ${total}`;
  }

  function add(raw) {
    const text = raw.trim();
    if (!text) return;
    todos.push({ id: uid(), text, done: false, createdAt: Date.now() });
    persist();
  }

  function toggle(id) {
    todos = todos.map(t => (t.id === id ? { ...t, done: !t.done } : t));
    persist();
  }

  function remove(id) {
    todos = todos.filter(t => t.id !== id);
    persist();
  }

  function setFilter(next) {
    if (next === filter) return;
    filter = next;
    [...filtersEl.querySelectorAll("button")].forEach(btn => {
      const on = btn.dataset.filter === filter;
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    render();
  }

  function persist() {
    Storage.save(todos);
    render();
  }

  form.addEventListener("submit", e => {
    e.preventDefault();
    add(input.value);
    input.value = "";
    input.focus();
  });

  filtersEl.addEventListener("click", e => {
    const btn = e.target.closest("button[data-filter]");
    if (btn) setFilter(btn.dataset.filter);
  });

  render();
})();
