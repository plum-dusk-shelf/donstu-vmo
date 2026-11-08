package main.java.dao;

import main.java.model.Category;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class CategoryDao {
    private final Connection connection;

    public CategoryDao(Connection connection) {
        this.connection = connection;
    }

    // Добавление новой категории
    public boolean addCategory(Category category) throws SQLException {
        String sql = "INSERT INTO category (name, description) VALUES (?, ?)";
        
        try (PreparedStatement statement = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            statement.setString(1, category.getName());
            statement.setString(2, category.getDescription());
            
            int affectedRows = statement.executeUpdate();
            
            if (affectedRows == 0) {
                throw new SQLException("Создание категории не удалось, ни одна запись не добавлена.");
            }
            
            try (ResultSet generatedKeys = statement.getGeneratedKeys()) {
                if (generatedKeys.next()) {
                    category.setId(generatedKeys.getInt(1));
                    return true;
                } else {
                    throw new SQLException("Создание категории не удалось, ID не получен.");
                }
            }
        }
    }

    // Получение всех категорий
    public List<Category> getAllCategories() throws SQLException {
        List<Category> categories = new ArrayList<>();
        String sql = "SELECT * FROM category ORDER BY name";
        
        try (Statement statement = connection.createStatement();
             ResultSet resultSet = statement.executeQuery(sql)) {
            
            while (resultSet.next()) {
                Category category = new Category();
                category.setId(resultSet.getInt("category_id"));
                category.setName(resultSet.getString("name"));
                category.setDescription(resultSet.getString("description"));
                categories.add(category);
            }
        }
        return categories;
    }

    // Получение категории по ID
    public Category getCategoryById(int id) throws SQLException {
        String sql = "SELECT * FROM category WHERE category_id = ?";
        
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, id);
            
            try (ResultSet resultSet = statement.executeQuery()) {
                if (resultSet.next()) {
                    Category category = new Category();
                    category.setId(resultSet.getInt("category_id"));
                    category.setName(resultSet.getString("name"));
                    category.setDescription(resultSet.getString("description"));
                    return category;
                }
            }
        }
        return null;
    }

    // Обновление категории
    public boolean updateCategory(Category category) throws SQLException {
        String sql = "UPDATE category SET name = ?, description = ? WHERE category_id = ?";
        
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setString(1, category.getName());
            statement.setString(2, category.getDescription());
            statement.setInt(3, category.getId());
            
            int affectedRows = statement.executeUpdate();
            return affectedRows > 0;
        }
    }

    // Удаление категории
    public boolean deleteCategory(int id) throws SQLException {
        String sql = "DELETE FROM category WHERE category_id = ?";
        
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, id);
            int affectedRows = statement.executeUpdate();
            return affectedRows > 0;
        }
    }

    // Проверка существования категории
    public boolean categoryExists(int id) throws SQLException {
        String sql = "SELECT category_id FROM category WHERE category_id = ?";
        
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, id);
            
            try (ResultSet resultSet = statement.executeQuery()) {
                return resultSet.next();
            }
        }
    }
}
