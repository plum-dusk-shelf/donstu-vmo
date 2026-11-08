package main.lab1;

import javafx.collections.FXCollections;
import javafx.fxml.FXML;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class GraphAppController {
    @FXML
    private ComboBox<String> functionComboBox;
    @FXML
    private TextField fromField;
    @FXML
    private TextField toField;
    @FXML
    private TextField stepField;
    @FXML
    private TextField widthField;
    @FXML
    private LineChart<Number, Number> chart;
    @FXML
    private VBox functionsList;

    private List<FunctionData> functions = new ArrayList<>();

    @FXML
    private void initialize() {
        // Инициализация выпадающего списка функций
        functionComboBox.setItems(FXCollections.observableArrayList(
                "x^2",
                "sin(x)",
                "cos(x)",
                "x^3",
                "sqrt(x)",
                "log(x)",
                "exp(x)"
        ));

        // Установка значений по умолчанию
        fromField.setText("-10");
        toField.setText("10");
        stepField.setText("0.1");
        widthField.setText("2");

        // Настройка графика
        chart.setTitle("Графики функций");
        chart.setAnimated(false);

        // Получаем оси из графика
        NumberAxis xAxis = (NumberAxis) chart.getXAxis();
        NumberAxis yAxis = (NumberAxis) chart.getYAxis();
        xAxis.setLabel("x");
        yAxis.setLabel("y");
    }

    @FXML
    private void addFunction() {
        try {
            String functionName = functionComboBox.getValue();
            if (functionName == null) {
                showAlert("Ошибка", "Выберите функцию");
                return;
            }

            double from = Double.parseDouble(fromField.getText());
            double to = Double.parseDouble(toField.getText());
            double step = Double.parseDouble(stepField.getText());
            double width = Double.parseDouble(widthField.getText());

            if (step <= 0) {
                showAlert("Ошибка", "Шаг должен быть положительным");
                return;
            }

            if (from >= to) {
                showAlert("Ошибка", "Начальное значение должно быть меньше конечного");
                return;
            }

            Function<Double, Double> function = getFunctionByName(functionName);
            if (function == null) {
                showAlert("Ошибка", "Неизвестная функция");
                return;
            }

            FunctionData functionData = new FunctionData(functionName, function, from, to, step, width);
            functions.add(functionData);
            addFunctionToUI(functionData);
            updateChart();

        } catch (NumberFormatException e) {
            showAlert("Ошибка", "Введите корректные числовые значения");
        }
    }

    private Function<Double, Double> getFunctionByName(String name) {
        switch (name) {
            case "x^2": return x -> x * x;
            case "sin(x)": return Math::sin;
            case "cos(x)": return Math::cos;
            case "x^3": return x -> x * x * x;
            case "sqrt(x)": return Math::sqrt;
            case "log(x)": return Math::log;
            case "exp(x)": return Math::exp;
            default: return null;
        }
    }

    private void addFunctionToUI(FunctionData functionData) {
        CheckBox checkBox = new CheckBox(functionData.getName());
        checkBox.setSelected(true);
        checkBox.setOnAction(e -> {
            functionData.setVisible(checkBox.isSelected());
            updateChart();
        });

        Button removeButton = new Button("Удалить");
        removeButton.setOnAction(e -> {
            functions.remove(functionData);
            functionsList.getChildren().remove(checkBox);
            functionsList.getChildren().remove(removeButton);
            updateChart();
        });

        functionsList.getChildren().addAll(checkBox, removeButton);
    }

    private void updateChart() {
        chart.getData().clear();

        for (FunctionData functionData : functions) {
            if (!functionData.isVisible()) continue;

            XYChart.Series<Number, Number> series = new XYChart.Series<>();
            series.setName(functionData.getName());

            for (double x = functionData.getFrom(); x <= functionData.getTo(); x += functionData.getStep()) {
                try {
                    double y = functionData.getFunction().apply(x);
                    series.getData().add(new XYChart.Data<>(x, y));
                } catch (Exception e) {
                    // Пропускаем точки, где функция не определена
                }
            }

            chart.getData().add(series);

            // Установка толщины линии
            if (series.getNode() != null) {
                series.getNode().setStyle("-fx-stroke-width: " + functionData.getWidth() + "px;");
            }
        }
    }

    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    private static class FunctionData {
        private String name;
        private Function<Double, Double> function;
        private double from;
        private double to;
        private double step;
        private double width;
        private boolean visible;

        public FunctionData(String name, Function<Double, Double> function, double from, double to, double step, double width) {
            this.name = name;
            this.function = function;
            this.from = from;
            this.to = to;
            this.step = step;
            this.width = width;
            this.visible = true;
        }

        public String getName() { return name; }
        public Function<Double, Double> getFunction() { return function; }
        public double getFrom() { return from; }
        public double getTo() { return to; }
        public double getStep() { return step; }
        public double getWidth() { return width; }
        public boolean isVisible() { return visible; }
        public void setVisible(boolean visible) { this.visible = visible; }
    }
}