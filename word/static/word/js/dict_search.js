document.addEventListener("DOMContentLoaded", function () {
    const tableContainer = document.getElementById("dictionary-table"); // тут забираем переданный id 
    if (!tableContainer) return;
  
    const highlightId = tableContainer.dataset.highlightId;
    const row = document.getElementById(`word-${highlightId}`);
    if (row) {
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      // Применим фон ко всем <td> внутри строки
      row.querySelectorAll("td").forEach(td => {
        td.style.backgroundColor = "#ffff99";
        td.style.transition = "background-color 0.5s ease";
      });
      setTimeout(() => {
        row.querySelectorAll("td").forEach(td => {
          td.style.backgroundColor = "";  // сбрасывает обратно к обычному
        });
      }, 2000);  // 2000 мс = 2 секунды
    }
  });