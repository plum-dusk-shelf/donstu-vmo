import java.lang.Math;
import java.text.DecimalFormat;

public class lab2_3{
	public static void main(String [] args){
		int R = 10;
		int r = 2;
		int x = Integer.parseInt(args[0]);
		int y = Integer.parseInt(args[1]);

		double dist = Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2));


		if (dist < R)
			System.out.println("Detected");
		else
			System.out.println("Do not detected");

		if (dist < r)
			System.out.println("Alarm!");
		

	}
}
