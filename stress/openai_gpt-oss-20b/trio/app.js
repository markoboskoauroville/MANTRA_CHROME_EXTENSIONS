document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('go');
  var out = document.getElementById('out');
  if (!btn || !out) return;
  btn.addEventListener('click', function () {
    out.textContent = 'done';
  });
});
