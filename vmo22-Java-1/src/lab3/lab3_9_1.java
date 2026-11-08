import java.util.regex.Pattern;

public class lab3_9_1 {
    public static void main(String[] args) {
        String[] phoneNumbers = {
            "+79043781661", "+7 904 378 1661", "+7 904 378 16 61",
            "+7-904-378-16-61", "+7(904)3781661", "+7(904) 378-16 61",
            "89043781661", "8 904 378-16-61",
        };

        String regex = "^(\\+7|8)\\s?\\(?\\d{3}\\)?\\s?\\d{3}\\s?-?\\d{2}\\s?-?\\d{2}$";
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

