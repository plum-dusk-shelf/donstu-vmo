import java.util.Scanner;

public class DecimalToBaseConverter {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Your number: ");
        int decimal = scanner.nextInt();
        System.out.println("Base: ");
        int base = scanner.nextInt();

        if (base < 2 || base > 8) {
            System.out.println("Wrong base");
            return;
        }

        System.out.println("In base " + base + " your number is: " + convertDecimalToBase(decimal, base));
    }

    public static String convertDecimalToBase(int decimal, int base) {
        StringBuilder result = new StringBuilder();
        while (decimal > 0) {
            result.insert(0, decimal % base);
            decimal = decimal / base;
        }
        return result.toString();
    }
}

