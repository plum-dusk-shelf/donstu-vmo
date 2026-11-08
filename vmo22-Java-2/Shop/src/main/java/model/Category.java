package main.java.model;

public class Category {
    private int id;
    private String name;
    private String description;

    // Конструкторы
    public Category() {
        // Пустой конструктор необходим для работы JSP, JPA и других фреймворков
    }

    public Category(int id, String name, String description) {
        this.id = id;
        this.name = name;
        this.description = description;
    }

    // Геттеры и сеттеры
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    // Переопределение toString() для удобства отладки
    @Override
    public String toString() {
        return "Category{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", description='" + description + '\'' +
                '}';
    }

    // Дополнительный метод для валидации
    public boolean isValid() {
        return name != null && !name.trim().isEmpty();
    }
}
