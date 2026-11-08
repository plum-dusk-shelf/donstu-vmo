
async function addItem() {
  const fileInput = document.getElementById("filename");
  const fileSize = document.getElementById("filesize");

  const url = new URL(`${location.origin}/api/gallery`);
  url.searchParams.set("filename", fileInput.value);
  url.searchParams.set("size", fileSize.value);

  const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=utf-8"
      },
  });

  if (response.ok) {
    await load(document.getElementById("sort").value);
  }

}


async function deleteItem(id) {
  console.log(id);

  const url = new URL(`${location.origin}/api/gallery`);
  url.searchParams.set("id", id);

  const response = await fetch(url, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json;charset=utf-8"
    },
  });

  if (response.ok) {
    await load(document.getElementById("sort").value);
  }
}


document.getElementById("sort").addEventListener("change", async (event) => {
  await load(event.target.value);
});

async function load(orderBy) {
  const params = {
    orderBy: orderBy,
  };

  const url = new URL(`${location.origin}/api/gallery`);
  Object.entries(params).forEach(([key, value]) => {
    if (value)
      url.searchParams.set(key, value);
  });
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json;charset=utf-8"
    },
  });

  const data = await response.json();

    const rows = document.getElementById("rows");

  rows.innerHTML = data.data.map((item) => {
    const date = new Date(item.created_at).toLocaleDateString();
    return `
      <tr>
        <td>${item.filename}</td>
        <td>${item.size}</td>
        <td>${date}</td>
        <td>
          <button class="button is-danger is-small" onclick="deleteItem('${item.id}')">Удалить</button>
        </td>
      </tr>
    `;
  }).join("");
}



document.addEventListener("DOMContentLoaded", async () => {
  await load(document.getElementById("sort").value);
  document.getElementById("addItemButton").addEventListener("click", addItem);

});
