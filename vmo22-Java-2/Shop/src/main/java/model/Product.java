package main.java.model;


public class Product {
    private int id;
    private String name;
    private String description;
    private double price;
    private int categoryId;
    private int manufacturerId;
    
    // Конструкторы
    public Product() {}
    
    public Product(int id, String name, String description, double price, 
                  int categoryId, int manufacturerId) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.price = price;
        this.categoryId = categoryId;
        this.manufacturerId = manufacturerId;
    }
    
    // Геттеры
    public int getId() {
        return id;
    }
    
    public String getName() {
        return name;
    }
    
    public String getDescription() {
        return description;
    }
    
    public double getPrice() {
        return price;
    }
    
    public int getCategoryId() {
        return categoryId;
    }
    
    public int getManufacturerId() {
        return manufacturerId;
    }
    
    // Сеттеры
    public void setId(int id) {
        this.id = id;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public void setPrice(double price) {
        this.price = price;
    }
    
    public void setCategoryId(int categoryId) {
        this.categoryId = categoryId;
    }
    
    public void setManufacturerId(int manufacturerId) {
        this.manufacturerId = manufacturerId;
    }
    
    // Переопределение метода toString() для удобства отладки
    @Override
    public String toString() {
        return "Product{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", description='" + description + '\'' +
                ", price=" + price +
                ", categoryId=" + categoryId +
                ", manufacturerId=" + manufacturerId +
                '}';
    }
}
