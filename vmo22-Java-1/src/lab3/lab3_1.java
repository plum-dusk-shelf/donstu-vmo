import java.lang.Math;

public class lab3_1 {
    public static void main(String[] args) {
        double start = Math.PI / 15;
        double end = Math.PI;
        double step = Math.PI / 15;

        int size = (int) Math.ceil((end - start) / step);
        double[] xValues = new double[size];

        for (int index = 0; index < size; index++) {
		double x = start + step * index;
            	xValues[index] = x;
        }

	System.out.print("\n      \t");
        // Print the array for verification
        for (double x : xValues) {
		System.out.printf("% 8.4f ", x);
        }

	System.out.print("\nsin(x)\t");

        for (double x : xValues) {
		System.out.printf("% 8.4f ", Math.sin(x));
        }

	System.out.print("\nfunc2\t");

        for (double x : xValues) {
        	double result = (Math.exp(x) / (x * Math.log(x)));
		System.out.printf("% 8.4f ", result);
        }
    }
}
