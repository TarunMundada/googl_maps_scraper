(async function() {
  const delay = ms => new Promise(r => setTimeout(r, ms));

  const scrollable = document.querySelector('div[role="feed"]');
  if (!scrollable) return alert("❌ Could not find listings section!");

  // --- Scroll to load all results ---
  let prev = 0, stable = 0;
  while (stable < 3) {
    scrollable.scrollTo(0, scrollable.scrollHeight);
    await delay(2000);
    if (scrollable.scrollHeight === prev) stable++;
    else stable = 0;
    prev = scrollable.scrollHeight;
  }

  // --- Parse listings ---
  const results = [];
  document.querySelectorAll("div.Nv2PK").forEach(card => {
    const name = card.querySelector("a.hfpxzc")?.getAttribute("aria-label") || "";
    const phone = card.querySelector("span.UsdlK")?.innerText || "";
    const rating = card.querySelector("span.MW4etd")?.innerText || "";
    const reviews = card.querySelector("span.UY7F9")?.innerText || "";

    // Get first non-Google website link
    let website = "";
    card.querySelectorAll("a").forEach(a => {
      const href = a.href;
      if (href.startsWith("http") && !href.includes("google.com")) {
        website = href;
      }
    });

    results.push({
      name,
      phone,
      rating: `${rating} ${reviews}`.trim(),
      address,
      website
    });
  });

  // --- Convert to CSV ---
  const csv = [
    ["Name", "Phone", "Rating" , "Website"],
    ...results.map(r => [r.name, r.phone, r.rating, r.website])
  ].map(row => row.map(v => `"${v.replace(/"/g, '""')}"`).join(",")).join("\n");

  // --- Trigger download ---
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "google_maps_listings.csv";
  a.click();
  URL.revokeObjectURL(url);

  alert(`✅ Scraped ${results.length} listings. File downloaded.`);
})();