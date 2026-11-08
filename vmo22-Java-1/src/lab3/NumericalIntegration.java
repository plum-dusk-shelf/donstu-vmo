public class NumericalIntegration {

    public static double leftRectangleRule(double[] xValues, double[] yValues) {
        double sum = 0.0;
        double h = xValues[1] - xValues[0];

        for (int i = 0; i < xValues.length - 1; i++) {
            sum += yValues[i];
        }

        return sum * h;
    }

    public static double function(double x) {
        return Math.exp(x) - Math.pow(x, 3);
    }

    public static void main(String[] args) {
        int n = 101;
        double a = 0.0;
        double b = 4.0;
        double h = (b - a) / (n - 1);

        double[] xValues = new double[n];
        double[] yValues = new double[n];

        for (int i = 0; i < n; i++) {
            xValues[i] = a + i * h;
            yValues[i] = function(xValues[i]);
        }

        double numericalIntegral = leftRectangleRule(xValues, yValues);
        double integral = Math.exp(4) - Math.pow(4, 4) / 4;

        System.out.println("Numerical integral: " + numericalIntegral);
        System.out.println("Analytical integral: " + integral);
        System.out.println("Difference: " + Math.abs(numericalIntegral - integral));
    }
}

