package main.lab1;

import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.control.Button;
import javafx.scene.control.ToggleButton;
import javafx.scene.control.ToggleGroup;
import javafx.scene.image.Image;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;

import javax.imageio.ImageIO;
import java.io.File;
import java.io.IOException;
import java.util.Objects;

public class MainController {

    @FXML
    private VBox toggleButtonContainer;

    @FXML
    private Canvas canvas;

    @FXML
    private Button saveButton;

    private ToggleGroup toggleGroup;
    private Image selectedImage;

    @FXML
    public void initialize() {
        toggleGroup = new ToggleGroup();

        // Загрузка изображений и создание ToggleButton для каждого изображения
        String[] imagePaths = {"/images/image1.png", "/images/image2.png", "/images/image3.png"};
        for (String path : imagePaths) {
            Image image = new Image(Objects.requireNonNull(getClass().getResourceAsStream(path)));
            ToggleButton toggleButton = new ToggleButton();
            toggleButton.setGraphic(new javafx.scene.image.ImageView(image));
            toggleButton.setToggleGroup(toggleGroup);
            toggleButton.setOnAction(event -> selectedImage = image);
            toggleButtonContainer.getChildren().add(toggleButton);
        }

        // Обработка кликов правой кнопкой мыши на Canvas
        canvas.addEventHandler(MouseEvent.MOUSE_CLICKED, event -> {
            if (event.getButton() == MouseButton.SECONDARY && selectedImage != null) {
                GraphicsContext gc = canvas.getGraphicsContext2D();
                gc.drawImage(selectedImage, event.getX() - selectedImage.getWidth() / 2, event.getY() - selectedImage.getHeight() / 2);
            }
        });

        // Обработка нажатия на кнопку "Сохранить"
        saveButton.setOnAction(event -> {
            FileChooser fileChooser = new FileChooser();
            fileChooser.setTitle("Save Image");
            fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("PNG files (*.png)", "*.png"));
            File file = fileChooser.showSaveDialog(canvas.getScene().getWindow());
            if (file != null) {
                try {
                    ImageIO.write(SwingFXUtils.fromFXImage(canvas.snapshot(null, null), null), "png", file);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });
    }
}