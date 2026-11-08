package main.lab1;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.input.MouseButton;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.shape.*;
import javafx.stage.Stage;
import javafx.geometry.Bounds;
import java.util.Random;

public class GraphicEditor extends Application {

    private static final int WIDTH = 800;
    private static final int HEIGHT = 600;
    private static final int INITIAL_SIZE = 100;
    private static final int MOVE_STEP = 5;
    private static final int RESIZE_STEP = 5;

    private Pane drawingArea;
    private Shape selectedShape;
    private Rectangle boundingBox;
    private ComboBox<String> shapeSelector;
    private ColorPicker colorPicker;
    private double dragStartX, dragStartY;

    @Override
    public void start(Stage primaryStage) {
        BorderPane root = new BorderPane();

        // Панель инструментов
        ToolBar toolBar = createToolBar();
        root.setTop(toolBar);

        // Область рисования
        drawingArea = new Pane();
        drawingArea.setStyle("-fx-background-color: white;");
        root.setCenter(drawingArea);

        // Инициализация рамки выделения (как в PrimitiveApp)
        boundingBox = new Rectangle();
        boundingBox.setFill(Color.TRANSPARENT);
        boundingBox.setStroke(Color.BLUE);
        boundingBox.getStrokeDashArray().addAll(5d, 5d);
        boundingBox.setStrokeWidth(1);
        boundingBox.setOpacity(0.5);
        boundingBox.setVisible(false);

        setupMouseHandlers();

        Scene scene = new Scene(root, WIDTH, HEIGHT);

        // Обработка клавиш (как в PrimitiveApp)
        scene.setOnKeyPressed(event -> {
            if (selectedShape == null) return;

            switch (event.getCode()) {
                case DELETE:
                    removeSelectedShape();
                    break;
                case UP:
                    moveSelectedShape(0, -MOVE_STEP);
                    break;
                case DOWN:
                    moveSelectedShape(0, MOVE_STEP);
                    break;
                case LEFT:
                    moveSelectedShape(-MOVE_STEP, 0);
                    break;
                case RIGHT:
                    moveSelectedShape(MOVE_STEP, 0);
                    break;
                case ADD:
                case PLUS:
                    resizeSelectedShape(0, RESIZE_STEP);
                    break;
                case SUBTRACT:
                case MINUS:
                    resizeSelectedShape(0, -RESIZE_STEP);
                    break;
                case LESS:
                case COMMA:
                    resizeSelectedShape(-RESIZE_STEP, 0);
                    break;
                case GREATER:
                case PERIOD:
                    resizeSelectedShape(RESIZE_STEP, 0);
                    break;
            }
        });

        primaryStage.setTitle("Графический редактор (как PrimitiveApp)");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private ToolBar createToolBar() {
        ToolBar toolBar = new ToolBar();

        shapeSelector = new ComboBox<>();
        shapeSelector.getItems().addAll("Отрезок", "Окружность", "Эллипс", "Прямоугольник");
        shapeSelector.setValue("Прямоугольник");

        colorPicker = new ColorPicker(Color.RED);

        Button addButton = new Button("Добавить");
        addButton.setOnAction(e -> addNewShape());

        Button deleteButton = new Button("Удалить");
        deleteButton.setOnAction(e -> removeSelectedShape());

        Button randomButton = new Button("Случайный");
        randomButton.setOnAction(e -> addRandomShape());

        toolBar.getItems().addAll(
                new Label("Примитив:"), shapeSelector,
                new Label("Цвет:"), colorPicker,
                addButton, deleteButton, randomButton
        );

        return toolBar;
    }

    private void setupMouseHandlers() {
        drawingArea.setOnMousePressed(event -> {
            if (event.getButton() == MouseButton.PRIMARY) {
                selectShapeAt(event.getX(), event.getY());

                if (selectedShape != null) {
                    dragStartX = event.getSceneX();
                    dragStartY = event.getSceneY();
                }
            }
        });

        drawingArea.setOnMouseDragged(event -> {
            if (selectedShape != null && event.getButton() == MouseButton.PRIMARY) {
                double offsetX = event.getSceneX() - dragStartX;
                double offsetY = event.getSceneY() - dragStartY;

                selectedShape.setTranslateX(selectedShape.getTranslateX() + offsetX);
                selectedShape.setTranslateY(selectedShape.getTranslateY() + offsetY);

                dragStartX = event.getSceneX();
                dragStartY = event.getSceneY();

                updateBoundingBox();
            }
        });
    }

    private void addNewShape() {
        String shapeType = shapeSelector.getValue();
        Color color = colorPicker.getValue();
        createShape(shapeType, color, WIDTH/2, HEIGHT/2, INITIAL_SIZE, INITIAL_SIZE);
    }

    private void addRandomShape() {
        Random random = new Random();
        String[] shapes = {"Отрезок", "Окружность", "Эллипс", "Прямоугольник"};
        String shapeType = shapes[random.nextInt(shapes.length)];
        Color color = Color.color(random.nextDouble(), random.nextDouble(), random.nextDouble());

        int x = 100 + random.nextInt(WIDTH - 200);
        int y = 100 + random.nextInt(HEIGHT - 200);
        int size = 50 + random.nextInt(100);

        createShape(shapeType, color, x, y, size, size);
    }

    private void createShape(String shapeType, Color color, double x, double y, double width, double height) {
        Shape shape = null;

        switch (shapeType) {
            case "Отрезок":
                shape = new Line(0, 0, width, height);
                break;
            case "Окружность":
                double radius = width / 2;
                shape = new Circle(radius);
                shape.setTranslateX(x - radius);
                shape.setTranslateY(y - radius);
                break;
            case "Эллипс":
                shape = new Ellipse(width / 2, height / 2);
                shape.setTranslateX(x - width / 2);
                shape.setTranslateY(y - height / 2);
                break;
            case "Прямоугольник":
                shape = new Rectangle(width, height);
                shape.setTranslateX(x - width / 2);
                shape.setTranslateY(y - height / 2);
                break;
        }

        if (shape != null) {
            shape.setFill(color);

            if (shapeType.equals("Отрезок")) {
                shape.setTranslateX(x - width / 2);
                shape.setTranslateY(y - height / 2);
            }

            shape.setOnMouseClicked(e -> selectShapeAt(e.getX(), e.getY()));
            drawingArea.getChildren().add(shape);
            selectShape(shape);
        }
    }

    private void selectShapeAt(double x, double y) {
        for (javafx.scene.Node node : drawingArea.getChildren()) {
            if (node instanceof Shape && node != boundingBox) {
                Shape shape = (Shape) node;
                if (shape.contains(shape.sceneToLocal(x, y))) {
                    selectShape(shape);
                    return;
                }
            }
        }
        selectShape(null);
    }

    private void selectShape(Shape shape) {
        if (selectedShape != null) {
            selectedShape.setStrokeWidth(0);
        }

        selectedShape = shape;

        if (selectedShape != null) {
            selectedShape.setStroke(Color.BLACK);
            selectedShape.setStrokeWidth(1);
            updateBoundingBox();
            boundingBox.setVisible(true);
        } else {
            boundingBox.setVisible(false);
        }
    }

    private void updateBoundingBox() {
        if (selectedShape != null) {
            Bounds bounds = selectedShape.getBoundsInParent();
            boundingBox.setX(bounds.getMinX() - 2);
            boundingBox.setY(bounds.getMinY() - 2);
            boundingBox.setWidth(bounds.getWidth() + 4);
            boundingBox.setHeight(bounds.getHeight() + 4);

            drawingArea.getChildren().remove(boundingBox);
            drawingArea.getChildren().add(boundingBox);
        }
    }

    private void moveSelectedShape(double dx, double dy) {
        if (selectedShape != null) {
            selectedShape.setTranslateX(selectedShape.getTranslateX() + dx);
            selectedShape.setTranslateY(selectedShape.getTranslateY() + dy);
            updateBoundingBox();
        }
    }

    private void resizeSelectedShape(double dw, double dh) {
        if (selectedShape != null) {
            if (selectedShape instanceof Line) {
                Line line = (Line) selectedShape;
                line.setEndX(line.getEndX() + dw);
                line.setEndY(line.getEndY() + dh);
            }
            else if (selectedShape instanceof Circle) {
                Circle circle = (Circle) selectedShape;
                double newRadius = circle.getRadius() + (dw + dh) / 2;
                if (newRadius > 0) {
                    circle.setRadius(newRadius);
                    // Корректируем позицию после изменения размера
                    circle.setTranslateX(circle.getTranslateX() - dw/2);
                    circle.setTranslateY(circle.getTranslateY() - dh/2);
                }
            }
            else if (selectedShape instanceof Ellipse) {
                Ellipse ellipse = (Ellipse) selectedShape;
                double newRadiusX = ellipse.getRadiusX() + dw/2;
                double newRadiusY = ellipse.getRadiusY() + dh/2;
                if (newRadiusX > 0 && newRadiusY > 0) {
                    ellipse.setRadiusX(newRadiusX);
                    ellipse.setRadiusY(newRadiusY);
                    // Корректируем позицию после изменения размера
                    ellipse.setTranslateX(ellipse.getTranslateX() - dw/2);
                    ellipse.setTranslateY(ellipse.getTranslateY() - dh/2);
                }
            }
            else if (selectedShape instanceof Rectangle) {
                Rectangle rect = (Rectangle) selectedShape;
                double newWidth = rect.getWidth() + dw;
                double newHeight = rect.getHeight() + dh;
                if (newWidth > 0 && newHeight > 0) {
                    rect.setWidth(newWidth);
                    rect.setHeight(newHeight);
                    // Корректируем позицию после изменения размера
                    rect.setTranslateX(rect.getTranslateX() - dw/2);
                    rect.setTranslateY(rect.getTranslateY() - dh/2);
                }
            }
            updateBoundingBox();
        }
    }

    private void removeSelectedShape() {
        if (selectedShape != null) {
            drawingArea.getChildren().remove(selectedShape);
            drawingArea.getChildren().remove(boundingBox);
            selectedShape = null;
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}