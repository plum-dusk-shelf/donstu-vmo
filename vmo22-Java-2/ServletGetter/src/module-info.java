module main.java {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.swing;
    requires java.xml.bind;
    requires javax.servlet.api;

    opens main.java to javafx.fxml;
    exports main.java;
}