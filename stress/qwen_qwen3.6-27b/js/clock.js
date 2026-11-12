setInterval(() => {
  const el = document.getElementById('now');
  if (!el) return;
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  el.textContent = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}, 1000);
