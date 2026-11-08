<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!DOCTYPE html>
<html>
<head>
  <title>Библиотека супер изображений</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
</head>
<body>
<div class="columns">
  <div class="column"></div>

  <div class="column box">
    <br>
    <div class="columns">
      <div class="column">

        <div class="field has-addons">
          <div class="control is-expanded">
            <div class="select is-fullwidth is-small">
              <label>
                <select id="sort">
                  <option value="filename">Имя файла</option>
                  <option value="size">Размер</option>
                  <option value="crated_at">Время создания</option>
                </select>
              </label>
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <button class="button is-small js-modal-trigger" data-target="addItemModal">
          Добавить
        </button>
      </div>
    </div>



    <table class="table is-striped is-fullwidth">
      <thead>
      <tr>
        <th>Имя файла</th>
        <th>Размер</th>
        <th>Время создания</th>
        <th>Управление</th>
      </tr>
      </thead>
      <tbody id="rows">

      </tbody>
    </table>
  </div>
  <div class="column"></div>
</div>
<script src="js/gallery.js"></script>
<script src="js/modal.js"></script>


<div id="addItemModal" class="modal">
  <div class="modal-background"></div>
  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">Добавление элемента</p>
      <button class="delete" aria-label="close"></button>
    </header>
    <section class="modal-card-body">
      <div class="field">
        <label class="label">Имя файла</label>
        <div class="control">
          <label for="filename"></label><input id="filename" class="input" type="text" placeholder="filename">
        </div>
      </div>

      <div class="field">
        <label class="label">Размер</label>
        <div class="control">
          <label for="filesize"></label><input id="filesize" class="input" type="text" placeholder="size">
        </div>
      </div>

    </section>
    <footer class="modal-card-foot">
      <button id="addItemButton" class="button is-success">Сохранить</button>
      <button class="button">Отмена</button>
    </footer>
  </div>
</div>

</body>
</html>