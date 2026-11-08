module main {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.swing;
    requires java.xml.bind;
    requires javax.servlet.api;

    opens main.lab1 to javafx.fxml;
    exports main.lab1;

    opens main.lab2 to javafx.fxml;
    exports main.lab2;
}