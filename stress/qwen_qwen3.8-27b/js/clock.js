(() => {
  const update = () => {
    const el = document.getElementById('now');
    if (!el) return;
    const d = new Date();
    const p = n => String(n).padStart(2, '0');
    el.textContent = `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
  };
  update();
  setInterval(update, 1000);
})();
