package lab6;

import javax.swing.*;
import java.awt.*;

public class Curve extends JPanel {
    private double[] xValues;
    private double[] yValues;
    private int width = 300;
    private int height = 300;

    public Curve() {
    }

    public void setData(double[] xValues, double[] yValues) {
        this.xValues = xValues;
        this.yValues = yValues;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (xValues == null || yValues == null || xValues.length != yValues.length) {
            return;
        }

        Graphics2D g2d = (Graphics2D) g;

        double xMin = xValues[0];
        double xMax = xValues[xValues.length - 1];
        double yMin = Math.pow(10, 10);
        double yMax = - Math.pow(10, 10);

        for (double y : yValues) {
            if (y < yMin) yMin = y;
            if (y > yMax) yMax = y;
        }

        int prevX = (int) ((xValues[0] - xMin) / (xMax - xMin) * width);
        int prevY = height - (int) ((yValues[0] - yMin) / (yMax - yMin) * height);

        g2d.drawLine(0, 0, 0, 300);
        g2d.drawLine(0, 150, 300, 150);
        g2d.setColor(Color.RED);

        for (int i = 1; i < xValues.length; i++) {
            int x = (int) ((xValues[i] - xMin) / (xMax - xMin) * width);
            int y = (int) ((yValues[i] - yMin) / (yMax - yMin) * height);
            g2d.drawLine(prevX, prevY, x, y);
            prevX = x;
            prevY = y;
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Curve Graph");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(300, 350);

            Curve curve = new Curve();
            frame.add(curve);

            int numPoints = 100;
            double[] xValues = new double[numPoints];
            double[] yValues = new double[numPoints];

            for (int i = 0; i < numPoints; i++) {
                double x = (2 * Math.PI / (numPoints - 1)) * i;
                xValues[i] = x;
                yValues[i] = Math.sin(x);
            }

            curve.setData(xValues, yValues);

            frame.setVisible(true);
        });
    }
}

