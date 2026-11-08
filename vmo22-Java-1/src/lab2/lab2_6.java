//import java.io.PrintWriter;
//
//public class lab2_6 {
//    public static void main(String[] args) {
//	int start = 0x400;
//	int rows = 16;
//	int columns = 16;
//    PrintWriter writer = new PrintWriter(".\\lab2_6.txt", "UTF-8");
//        for (int i = 0; i < rows; i++) {
//            for (int j = 0; j < columns; j++) {
//                writer.printf("%04x: %c ", start + i * columns + j, Character.toChars(start + i * columns + j));
//            }
//            System.out.println();
//        }
//	writer.close();
//    }
//}
//
