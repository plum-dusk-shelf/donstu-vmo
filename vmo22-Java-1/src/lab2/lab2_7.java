public class lab2_7 {
    public static void main(String[] args) {
        String str = "абв abcd 12345";
        int lowerCaseLetters = 0;
        int upperCaseLetters = 0;
        int digits = 0;
        int arabicDigits = 0;
        int nonArabicDigits = 0;
        int otherCharacters = 0;

        for(int i=0; i<str.length(); i++) {
            char ch = str.charAt(i);
            if(Character.isLowerCase(ch)) {
                lowerCaseLetters++;
            }
	    if(Character.isUpperCase(ch)) {
                upperCaseLetters++;
            }
	    if(Character.isDigit(ch)) {
                digits++;
                if(ch >= '0' && ch <= '9') {
                    arabicDigits++;
                } else {
                    nonArabicDigits++;
                }
            } else {
                otherCharacters++;
            }
        }

        System.out.println("Lowercase letters: " + lowerCaseLetters);
        System.out.println("Uppercase letters: " + upperCaseLetters);
        System.out.println("Digits: " + digits);
        System.out.println("Arabic digits: " + arabicDigits);
        System.out.println("Non-Arabic digits: " + nonArabicDigits);
        System.out.println("Other characters: " + otherCharacters);
    }
}

