package lab7;

import javax.swing.*;
import java.awt.*;

public class CustomPanel extends JPanel {
    private JLabel firstLabel;
    private JLabel secondLabel;
    private JLabel thirdLabel;

    public CustomPanel() {
        firstLabel = new JLabel("Upper Label");
        secondLabel = new JLabel("Down Label");
        thirdLabel = new JLabel("Center Label");

        Font upperDownFont = new Font("dialog", Font.BOLD | Font.ITALIC, 10);
        Font centerFont = new Font("dialog", Font.BOLD, 18);

        firstLabel.setFont(upperDownFont);
        secondLabel.setFont(upperDownFont);
        thirdLabel.setFont(centerFont);

        firstLabel.setHorizontalAlignment(SwingConstants.LEFT);
        secondLabel.setHorizontalAlignment(SwingConstants.RIGHT);
        thirdLabel.setHorizontalAlignment(SwingConstants.CENTER);

        setLayout(new BorderLayout());
        add(firstLabel, BorderLayout.NORTH);
        add(secondLabel, BorderLayout.SOUTH);
        add(thirdLabel, BorderLayout.CENTER);

        setBackground(Color.LIGHT_GRAY);
    }


    public static void main(String[] args) {
        JFrame frame = new JFrame("Custom Panel Test");
        CustomPanel panel = new CustomPanel();


        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 300);
        frame.add(panel);
        frame.setVisible(true);
    }
}
