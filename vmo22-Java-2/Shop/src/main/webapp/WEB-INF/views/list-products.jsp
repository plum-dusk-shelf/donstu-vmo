<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<html>
<head>
    <title>Список товаров</title>
</head>
<body>
    <h1>Список товаров</h1>
    <a href="products?action=new">Добавить новый товар</a>
    <table border="1">
        <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Описание</th>
            <th>Цена</th>
            <th>Действия</th>
        </tr>
        <c:forEach var="product" items="${products}">
            <tr>
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>${product.description}</td>
                <td>${product.price}</td>
                <td>
                    <a href="products?action=edit&id=${product.id}">Редактировать</a>
                    <a href="products?action=delete&id=${product.id}">Удалить</a>
                </td>
            </tr>
        </c:forEach>
    </table>
</body>
</html>
