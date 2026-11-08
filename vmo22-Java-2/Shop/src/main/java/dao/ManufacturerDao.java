package main.java.dao;

import main.java.model.Manufacturer;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class ManufacturerDao {
    private Connection connection;

    public ManufacturerDao(Connection connection) {
        this.connection = connection;
    }

    public List<Manufacturer> getAllManufacturers() throws SQLException {
        List<Manufacturer> manufacturers = new ArrayList<>();
        String sql = "SELECT * FROM manufacturer";
        
        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                Manufacturer manufacturer = new Manufacturer();
                manufacturer.setId(rs.getInt("manufacturer_id"));
                manufacturer.setName(rs.getString("name"));
                manufacturers.add(manufacturer);
            }
        }
        return manufacturers;
    }
}
