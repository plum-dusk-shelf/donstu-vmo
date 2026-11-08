module com.lab5 {
    requires jakarta.faces;          // JSF
    requires jakarta.cdi;            // CDI
    requires jakarta.servlet;        // Servlet API
    requires jakarta.validation;    // Bean Validation
    requires java.naming;           // Для @Named и других аннотаций
	requires jakarta.inject;       // Для @Inject
    
    // Экспортируем пакеты, которые должны быть видны другим модулям
    //exports com.lab5.beans;
    //exports com.lab5.validators;
    
    // Разрешаем рефлексию (нужно для CDI и JSF)
    opens com.lab5.beans to jakarta.faces, jakarta.cdi, weld.core;
    opens com.lab5.validators to jakarta.faces;
}
