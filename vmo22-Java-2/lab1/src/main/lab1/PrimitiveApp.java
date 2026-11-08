package main.lab1;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.layout.Pane;
import javafx.scene.shape.*;
import javafx.scene.paint.Color;
import javafx.stage.Stage;
import java.util.Random;

public class PrimitiveApp extends Application {

    private static final int WIDTH = 600;
    private static final int HEIGHT = 400;
    private static final int INITIAL_SIZE = 100;
    private static final int MOVE_STEP = 5;
    private static final int RESIZE_STEP = 5;

    private Shape primitive;
    private Rectangle boundingBox;
    private double x = WIDTH / 2;
    private double y = HEIGHT / 2;
    private double width = INITIAL_SIZE;
    private double height = INITIAL_SIZE;

    @Override
    public void start(Stage primaryStage) {
        Pane root = new Pane();

        // Создаем случайный примитив
        createRandomPrimitive();

        // Создаем полупрозрачную пунктирную рамку
        boundingBox = new Rectangle();
        boundingBox.setFill(Color.TRANSPARENT);
        boundingBox.setStroke(Color.BLUE);
        boundingBox.getStrokeDashArray().addAll(5d, 5d);
        boundingBox.setStrokeWidth(1);
        boundingBox.setOpacity(0.5);

        updateShapes();

        root.getChildren().addAll(boundingBox, primitive);

        Scene scene = new Scene(root, WIDTH, HEIGHT);

        // Обработка клавиш
        scene.setOnKeyPressed(event -> {
            switch (event.getCode()) {
                case UP:
                    y -= MOVE_STEP;
                    break;
                case DOWN:
                    y += MOVE_STEP;
                    break;
                case LEFT:
                    x -= MOVE_STEP;
                    break;
                case RIGHT:
                    x += MOVE_STEP;
                    break;
                case ADD:
                case PLUS:
                    height += RESIZE_STEP;
                    break;
                case SUBTRACT:
                case MINUS:
                    height -= RESIZE_STEP;
                    break;
                case LESS:
                case COMMA:
                    width -= RESIZE_STEP;
                    break;
                case GREATER:
                case PERIOD:
                    width += RESIZE_STEP;
                    break;
                default:
                    break;
            }

            // Гарантируем, что размеры не станут отрицательными
            width = Math.max(10, width);
            height = Math.max(10, height);

            updateShapes();
        });

        primaryStage.setTitle("2D Primitive with Bounding Box");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private void createRandomPrimitive() {
        Random random = new Random();
        int type = random.nextInt(4);

        switch (type) {
            case 0: // Отрезок прямой
                primitive = new Line(0, 0, width, height);
                break;
            case 1: // Окружность
                double radius = Math.min(width, height) / 2;
                primitive = new Circle(radius, radius, radius);
                break;
            case 2: // Эллипс
                primitive = new Ellipse(width / 2, height / 2, width / 2, height / 2);
                break;
            case 3: // Прямоугольник
                primitive = new Rectangle(width, height);
                break;
        }

        primitive.setFill(Color.RED);
    }

    private void updateShapes() {
        // Обновляем положение примитива
        primitive.setTranslateX(x - width / 2);
        primitive.setTranslateY(y - height / 2);

        // Обновляем рамку
        boundingBox.setX(x - width / 2);
        boundingBox.setY(y - height / 2);
        boundingBox.setWidth(width);
        boundingBox.setHeight(height);
    }

    public static void main(String[] args) {
        launch(args);
    }
}