(function () {
  function pad(num) {
    return String(num).padStart(2, '0');
  }

  function updateTime() {
    var el = document.getElementById('now');
    if (!el) return;
    var now = new Date();
    var formatted = pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
    el.textContent = formatted;
  }

  // Initial call
  updateTime();
  // Update every second
  setInterval(updateTime, 1000);
})();
