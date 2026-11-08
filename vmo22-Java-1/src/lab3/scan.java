import java.util.Scanner;
public class scan{
	public static void main(String[] args){
		Scanner scan = new Scanner(System.in);
		String myLine = new String();
		if(scan.hasNextLine()) myLine = scan.nextLine();
		System.out.println(myLine);

	}
}
