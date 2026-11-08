public class lab2_5 {
    public static void main(String[] args) {
	    int num = Integer.parseInt(args[0]);
	    String binary = Integer.toOctalString(num);
	    String octal = Integer.toBinaryString(num);
	    String hex = Integer.toHexString(num);
	    System.out.format("%s %s %s", binary, octal, hex);
    }
}

