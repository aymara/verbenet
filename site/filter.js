// Live filtering for the class and verb indexes.
// <input class="filter" data-target="CSS selector of rows" [data-prefix]>
// Rows carry a lowercase, accent-free data-search attribute.
(function () {
  function fold(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").trim();
  }
  document.querySelectorAll("input.filter").forEach(function (input) {
    var rows = document.querySelectorAll(input.dataset.target);
    var prefix = input.hasAttribute("data-prefix");
    var count = input.parentNode.querySelector(".filter-count");
    function apply() {
      var q = fold(input.value), shown = 0;
      rows.forEach(function (row) {
        var s = row.dataset.search;
        var ok = !q || (prefix ? s.startsWith(q) : s.indexOf(q) !== -1);
        row.hidden = !ok;
        if (ok) shown++;
      });
      document.querySelectorAll("section.letter").forEach(function (sec) {
        sec.hidden = !sec.querySelector("li:not([hidden])");
      });
      if (count) count.textContent = q ? shown + " of " + rows.length : "";
    }
    input.addEventListener("input", apply);
    var q = new URLSearchParams(location.search).get("q");
    if (q) { input.value = q; }
    apply();
  });
})();
