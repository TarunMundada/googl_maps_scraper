document.getElementById("scrape").addEventListener("click", async () => {
  const status = document.getElementById("status");
  status.textContent = "Scraping... please wait";

  const tabs = await browser.tabs.query({ active: true, currentWindow: true });
  browser.tabs.executeScript(tabs[0].id, { file: "content.js" });

  status.textContent = "✅ Done! CSV will download automatically.";
});