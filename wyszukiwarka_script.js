document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("google_search");
  const list = document.getElementById("autocomplete-list");
  if (!input || !list) return;

  const headerOffset = 100; 

  function scrollToElementWithOffset(el, offset) {
    const elementPosition = el.getBoundingClientRect().top + window.pageYOffset;
    const offsetPosition = elementPosition - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth"
    });
  }

  const staticSuggestions = [
    { name: "Symulacja ekosystemy", url: "symulacja_ekosystemy.html" },
    { name: "Gra w życie", url: "gra_w_zycie.html" },
    { name: "Python: co to?", url: "python.html" },
    { name: "O mnie", url: "omnie.html" }
  ];

  const headingSuggestions = Array.from(document.querySelectorAll("h2")).map(el => ({
    name: el.innerText,
    scrollTo: el
  }));

  const suggestions = [...staticSuggestions, ...headingSuggestions];

  let currentFocus = -1;

  input.addEventListener("input", () => {
    const query = input.value.toLowerCase();
    list.innerHTML = "";
    currentFocus = -1;

    if (!query) return;

    const filtered = suggestions
      .filter(item => item.name.toLowerCase().includes(query))
      .slice(0, 8);

    filtered.forEach(item => {
      const div = document.createElement("div");
      div.classList.add("autocomplete-item");
      div.innerHTML = `<strong>${item.name.substr(0, query.length)}</strong>${item.name.substr(query.length)}`;

      div.addEventListener("click", () => {
        input.value = item.name;
        list.innerHTML = "";

        if (item.url) {
          window.location.href = item.url;
        } else if (item.scrollTo) {
          scrollToElementWithOffset(item.scrollTo, headerOffset);
        }
      });

      list.appendChild(div);
    });
  });

  input.addEventListener("keydown", function (e) {
    const items = list.getElementsByClassName("autocomplete-item");
    if (items.length === 0) return;

    if (e.key === "ArrowDown") {
      currentFocus++;
      if (currentFocus >= items.length) currentFocus = 0;
      addActive(items);
      e.preventDefault();
    } else if (e.key === "ArrowUp") {
      currentFocus--;
      if (currentFocus < 0) currentFocus = items.length - 1;
      addActive(items);
      e.preventDefault();
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (currentFocus > -1) {
        items[currentFocus].click();
      }
    }
  });

  function addActive(items) {
    removeActive(items);
    if (currentFocus >= items.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = items.length - 1;
    items[currentFocus].classList.add("autocomplete-active");
  }

  function removeActive(items) {
    for (let item of items) {
      item.classList.remove("autocomplete-active");
    }
  }
});
