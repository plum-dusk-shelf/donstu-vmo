package lab7;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Arrays;

public class MyApp extends JFrame {
    public MyApp() {
        setTitle("My Swing Application");
        setSize(800, 400);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        JLabel label = new JLabel("Пример метки");
        JButton button = new JButton("Кнопка");
        JCheckBox checkBox = new JCheckBox("Флажок");

        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Bomb has been");
            }
        });

        JRadioButton radioButton1 = new JRadioButton("Радиокнопка1");
        JRadioButton radioButton2 = new JRadioButton("Радиокнопка2");

        ButtonGroup group = new ButtonGroup();
        group.add(radioButton1);
        group.add(radioButton2);

        String[] columnNames = {"Язык", "Автор", "Год"};
        Object[][] data = {
                {"Си", "Деннис Ритчи", 1972},
                {"C++", "Бьерн Страуструп", 1983},
                {"Python", "Гвидо ван Россум", 1991},
                {"Java", "Джеймс Гослинг", 1995},
                {"JavaScript", "Брендон Айк", 1995},
                {"C#", "Андерс Хейлсберг", 2001},
                {"Scala", "Мартин Одерски", 2003}
        };
        JTable table = new JTable(new DefaultTableModel(data, columnNames));
        JScrollPane scrollPane = new JScrollPane(table);

        UIManager.LookAndFeelInfo[] lafs = UIManager.getInstalledLookAndFeels();
        JComboBox<String> lafComboBox = new JComboBox<>(Arrays.stream(lafs).map(UIManager.LookAndFeelInfo::getName).toArray(String[]::new));

            lafComboBox.addActionListener(e -> {
            String selectedLaf = (String) lafComboBox.getSelectedItem();
            try {
                for (UIManager.LookAndFeelInfo lafInfo : lafs) {
                    if (lafInfo.getName().equals(selectedLaf)) {
                        UIManager.setLookAndFeel(lafInfo.getClassName());
                        SwingUtilities.updateComponentTreeUI(MyApp.this);
                        break;
                    }
                }
            }
            catch (Exception ex) {ex.printStackTrace();}
        });

        JPanel panel = new JPanel(new FlowLayout());
        panel.add(lafComboBox);
        panel.add(label);
        panel.add(button);
        panel.add(checkBox);
        panel.add(radioButton1);
        panel.add(radioButton2);

        add(panel, BorderLayout.NORTH);
        add(scrollPane, BorderLayout.CENTER);
    }

    public static void main(String[] args) {
        new MyApp().setVisible(true);
    }
}
