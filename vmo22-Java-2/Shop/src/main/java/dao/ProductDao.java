package main.java.dao;

import main.java.model.Product;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class ProductDao {
    private Connection connection;
    
    public ProductDao(Connection connection) {
        this.connection = connection;
    }
    
    public List<Product> getAllProducts() throws SQLException {
    List<Product> products = new ArrayList<>();
    String sql = "SELECT * FROM product";
    
    try (Statement stmt = connection.createStatement();
         ResultSet rs = stmt.executeQuery(sql)) {
        
        while (rs.next()) {
            Product product = new Product();
            product.setId(rs.getInt("product_id"));
            product.setName(rs.getString("name"));
            product.setDescription(rs.getString("description"));
            product.setPrice(rs.getDouble("price"));
            product.setCategoryId(rs.getInt("category_id"));
            product.setManufacturerId(rs.getInt("manufacturer_id"));
            products.add(product);
        }
    }
    return products;
}

	public void close() throws SQLException {
    if (connection != null && !connection.isClosed()) {
        connection.close();
    }
}
    
    public void addProduct(Product product) throws SQLException {
        String sql = "INSERT INTO product (name, description, price, category_id, manufacturer_id) VALUES (?, ?, ?, ?, ?)";
        
        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, product.getName());
            pstmt.setString(2, product.getDescription());
            pstmt.setDouble(3, product.getPrice());
            pstmt.setInt(4, product.getCategoryId());
            pstmt.setInt(5, product.getManufacturerId());
            pstmt.executeUpdate();
        }
    }
    
    public void updateProduct(Product product) throws SQLException {
        String sql = "UPDATE product SET name = ?, description = ?, price = ?, category_id = ?, manufacturer_id = ? WHERE product_id = ?";
        
        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, product.getName());
            pstmt.setString(2, product.getDescription());
            pstmt.setDouble(3, product.getPrice());
            pstmt.setInt(4, product.getCategoryId());
            pstmt.setInt(5, product.getManufacturerId());
            pstmt.setInt(6, product.getId());
            pstmt.executeUpdate();
        }
    }
	public boolean deleteProduct(int id) throws SQLException {
        // Используем существующее соединение
        try {
            connection.setAutoCommit(false); // Начало транзакции

            // 1. Удаляем со склада
            try (PreparedStatement stmt = connection.prepareStatement(
                    "DELETE FROM warehouse WHERE product_id = ?")) {
                stmt.setInt(1, id);
                stmt.executeUpdate();
            }

            // 2. Удаляем товар
            try (PreparedStatement stmt = connection.prepareStatement(
                    "DELETE FROM product WHERE product_id = ?")) {
                stmt.setInt(1, id);
                int affectedRows = stmt.executeUpdate();
                connection.commit(); // Подтверждаем транзакцию
                return affectedRows > 0;
            }
        } catch (SQLException e) {
            connection.rollback(); // Откат при ошибке
            throw e;
        } finally {
            connection.setAutoCommit(true); // Возвращаем авто-коммит
        }
    }
    
    
    public Product getProductById(int id) throws SQLException {
        String sql = "SELECT * FROM product WHERE product_id = ?";
        Product product = null;
        
        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            ResultSet rs = pstmt.executeQuery();
            
            if (rs.next()) {
                product = new Product(
                    rs.getInt("product_id"),
                    rs.getString("name"),
                    rs.getString("description"),
                    rs.getDouble("price"),
                    rs.getInt("category_id"),
                    rs.getInt("manufacturer_id")
                );
            }
        }
        return product;
    }
}
