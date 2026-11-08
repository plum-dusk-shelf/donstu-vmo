module main.java {
    requires jakarta.servlet;
    requires jakarta.xml.bind;

    // Экспортируем пакет с вашими классами, если они используются в JSP/других модулях
    exports main.java;

    // Открываем пакет для рефлексии (нужно для JAXB)
    opens main.java to jakarta.xml.bind;
    exports main.java.com.example;
    opens main.java.com.example to jakarta.xml.bind;
}