<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<html>
<head>
    <title>Редактировать товар</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"],
        input[type="number"],
        select,
        textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        .btn {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .back-link {
            display: inline-block;
            margin-top: 15px;
            color: #333;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Редактировать товар</h1>
        
        <form action="products" method="post">
            <input type="hidden" name="action" value="update">
            <input type="hidden" name="id" value="${product.id}">
            
            <div class="form-group">
                <label for="name">Название товара:</label>
                <input type="text" id="name" name="name" value="${product.name}" required>
            </div>
            
            <div class="form-group">
                <label for="description">Описание:</label>
                <textarea id="description" name="description">${product.description}</textarea>
            </div>
            
            <div class="form-group">
                <label for="price">Цена:</label>
                <input type="number" id="price" name="price" step="0.01" min="0" 
                       value="${product.price}" required>
            </div>
            
            <div class="form-group">
                <label for="categoryId">Категория:</label>
                <select id="categoryId" name="categoryId" required>
                    <option value="">-- Выберите категорию --</option>
                    <c:forEach items="${categories}" var="category">
                        <option value="${category.id}" 
                                ${product.categoryId == category.id ? 'selected' : ''}>
                            ${category.name}
                        </option>
                    </c:forEach>
                </select>
            </div>
            
            <div class="form-group">
                <label for="manufacturerId">Производитель:</label>
                <select id="manufacturerId" name="manufacturerId" required>
                    <option value="">-- Выберите производителя --</option>
                    <c:forEach items="${manufacturers}" var="manufacturer">
                        <option value="${manufacturer.id}" 
                                ${product.manufacturerId == manufacturer.id ? 'selected' : ''}>
                            ${manufacturer.name}
                        </option>
                    </c:forEach>
                </select>
            </div>
            
            <button type="submit" class="btn">Сохранить изменения</button>
        </form>
        
        <a href="products" class="back-link">← Вернуться к списку товаров</a>
    </div>
</body>
</html>
