package lab6;

import java.awt.*;
import java.awt.event.*;
import java.awt.geom.Line2D;

public class SinGraph extends Frame {
    public SinGraph() {
        setTitle("Sin Graph");
        setSize(300, 300);
        addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) {
                dispose();
            }
        });
    }

    @Override
    public void paint(Graphics g) {
        Graphics2D g2d = (Graphics2D) g;

        g2d.drawLine(150, 0, 150, 300);
        g2d.drawLine(0, 150, 300, 150);

        g2d.setColor(Color.RED);
        double scale = 300/(2 * Math.PI);
        for (int x = -150; x < 150; x++) {
            double xVal = x / scale ; // Scale x to range from -π to π
            double yVal = Math.sin(xVal) * scale; // Scale y to fit within the window
            g2d.draw(new Line2D.Double(x + 150, 150 - yVal, x + 151, 150 - Math.sin((x + 1) / scale) * scale));
        }
    }

    public static void main(String[] args) {
        SinGraph sineWave = new SinGraph();
        sineWave.setVisible(true);
    }
}
