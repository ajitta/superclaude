const Storage = {
  KEY: "todos.v1",

  load() {
    try {
      const raw = localStorage.getItem(this.KEY);
      const data = raw ? JSON.parse(raw) : [];
      return Array.isArray(data) ? data : [];
    } catch {
      return [];
    }
  },

  save(todos) {
    try {
      localStorage.setItem(this.KEY, JSON.stringify(todos));
    } catch (e) {
      console.warn("저장 실패:", e);
    }
  }
};
