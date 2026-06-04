async function initSearch() {
  const input = document.querySelector("#site-search");
  const results = document.querySelector("#search-results");
  if (!input || !results) return;

  const siteBase = document.body.dataset.siteBase || "/";
  const indexURL = document.body.dataset.searchIndex || `${siteBase}search-index.json`;
  const response = await fetch(indexURL).catch(() => null);
  if (!response || !response.ok) return;
  const pages = await response.json();

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    results.innerHTML = "";
    if (!query) return;

    const matches = pages
      .filter((page) => `${page.title} ${page.category} ${page.source}`.toLowerCase().includes(query))
      .slice(0, 8);

    if (matches.length === 0) {
      results.innerHTML = '<p class="empty-result">没有匹配结果</p>';
      return;
    }

    for (const page of matches) {
      const item = document.createElement("a");
      item.href = `${siteBase}${page.path}`;
      item.innerHTML = `<span>${page.category}</span><strong>${page.title}</strong>`;
      results.appendChild(item);
    }
  });
}

initSearch();
