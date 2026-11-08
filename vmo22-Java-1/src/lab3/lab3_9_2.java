import java.util.regex.Pattern;

public class lab3_9_2 {
    public static void main(String[] args) {
        String[] phoneNumbers = { "220-30-40", "8904-378-16-61", "Мои номера 220-30-40 и 8904-378-16-61 не считая служебных"
        };

        String regex = "\\b[23](?:[- ]?\\d{2}){3}\\b";
        Pattern pattern = Pattern.compile(regex);

        for (String phoneNumber : phoneNumbers) {
            if (pattern.matcher(phoneNumber).matches()) {
                System.out.println(phoneNumber + " is valid.");
            } else {
                System.out.println(phoneNumber + " is invalid.");
            }
        }
    }
}

