package main.java.model;

public class Manufacturer {
    private int id;
    private String name;
    private String country;
    private String website;

    // Конструкторы
    public Manufacturer() {
    }

    public Manufacturer(int id, String name, String country, String website) {
        this.id = id;
        this.name = name;
        this.country = country;
        this.website = website;
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

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public String getWebsite() {
        return website;
    }

    public void setWebsite(String website) {
        this.website = website;
    }

    // Переопределение toString() для удобства отладки
    @Override
    public String toString() {
        return "Manufacturer{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", country='" + country + '\'' +
                ", website='" + website + '\'' +
                '}';
    }

    // Дополнительные методы, если необходимо
    public boolean isValid() {
        return name != null && !name.trim().isEmpty();
    }
}
