package lab6;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

public class Mouse extends JFrame {
    private Color currentColor = Color.BLACK;
    private JLabel coordinatesLabel;

    public Mouse() {
        setTitle("Mouse Coordinates App");
        setSize(400, 300);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        coordinatesLabel = new JLabel("Click to see coordinates");
        coordinatesLabel.setHorizontalAlignment(SwingConstants.CENTER);
        add(coordinatesLabel, BorderLayout.CENTER);

        addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                int x = e.getX();
                int y = e.getY();
                coordinatesLabel.setText("Coordinates: (" + x + ", " + y + ")");
            }
        });

        addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                switch (e.getKeyChar()) {
                    case 'b':
                        currentColor = Color.BLACK;
                        coordinatesLabel.setForeground(currentColor);
                        break;
                    case 'w':
                        currentColor = Color.WHITE;
                        coordinatesLabel.setForeground(currentColor);
                        break;
                    case 'r':
                        currentColor = Color.RED;
                        coordinatesLabel.setForeground(currentColor);
                        break;
                    case 'g':
                        currentColor = Color.GREEN;
                        coordinatesLabel.setForeground(currentColor);
                        break;
                    case 'o':
                        currentColor = Color.ORANGE;
                        coordinatesLabel.setForeground(currentColor);
                        break;
                }
            }
        });

        setFocusable(true);
        requestFocusInWindow();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            Mouse app = new Mouse();
            app.setVisible(true);
        });
    }
}
