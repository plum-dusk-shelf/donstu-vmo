package lab7;

import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Random;

public class Dice extends JComponent {
    private boolean active = true;
    private int numberOfDots = new Random().nextInt(6) + 1;

    public Dice() {
        addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (active) {
                    numberOfDots = new Random().nextInt(6) + 1;
                    repaint();
                }
            }
        });
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        int width = getWidth();
        int height = getHeight();
        int dotSize = 20;

        g.setColor(Color.WHITE);
        g.fillRect(0, 0, width, height);

        g.setColor(Color.BLACK);
        switch (numberOfDots) {
            case 1:
                drawDot(g, width / 2, height / 2, dotSize);
                break;
            case 2:
                drawDot(g, width / 4, height / 4, dotSize);
                drawDot(g, 3 * width / 4, 3 * height / 4, dotSize);
                break;
            case 3:
                drawDot(g, width / 4, height / 4, dotSize);
                drawDot(g, width / 2, height / 2, dotSize);
                drawDot(g, 3 * width / 4, 3 * height / 4, dotSize);
                break;
            case 4:
                drawDot(g, width / 4, height / 4, dotSize);
                drawDot(g, 3 * width / 4, height / 4, dotSize);
                drawDot(g, width / 4, 3 * height / 4, dotSize);
                drawDot(g, 3 * width / 4, 3 * height / 4, dotSize);
                break;
            case 5:
                drawDot(g, width / 4, height / 4, dotSize);
                drawDot(g, 3 * width / 4, height / 4, dotSize);
                drawDot(g, width / 2, height / 2, dotSize);
                drawDot(g, width / 4, 3 * height / 4, dotSize);
                drawDot(g, 3 * width / 4, 3 * height / 4, dotSize);
                break;
            case 6:
                drawDot(g, width / 4, height / 4, dotSize);
                drawDot(g, 3 * width / 4, height / 4, dotSize);
                drawDot(g, width / 4, height / 2, dotSize);
                drawDot(g, 3 * width / 4, height / 2, dotSize);
                drawDot(g, width / 4, 3 * height / 4, dotSize);
                drawDot(g, 3 * width / 4, 3 * height / 4, dotSize);
                break;
        }
    }

    private void drawDot(Graphics g, int x, int y, int size) {
        g.fillOval(x - size / 2, y - size / 2, size, size);
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Dice");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(200, 200);

        Dice dice = new Dice();
        frame.add(dice);

        frame.setVisible(true);
    }
}
