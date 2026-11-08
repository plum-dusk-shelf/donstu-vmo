import java.util.Scanner;

public class CircleIntersection {
    private double x1, y1, r1, x2, y2, r2;

    public CircleIntersection(double x1, double y1, double r1, double x2, double y2, double r2) {
        this.x1 = x1;
        this.y1 = y1;
        this.r1 = r1;
        this.x2 = x2;
        this.y2 = y2;
        this.r2 = r2;
    }
	
    enum types {notInters, same, firstInside, secondInside, onePoint, twoPoints};

    public types checkIntersection() {
        double distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));

        if (distance > r1 + r2)
            return types.notInters;
        else if (distance < Math.abs(r1 - r2))
            return (r1 > r2) ? types.firstInside : types.secondInside;
        else if (distance == 0 && r1 == r2)
            return types.same;
        else if (distance == r1 + r2 || distance == Math.abs(r1 - r2))
            return types.onePoint;
	else
            return types.twoPoints; 
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("First circle:");
        double x1 = scanner.nextDouble();
        double y1 = scanner.nextDouble();
        double r1 = scanner.nextDouble();

        System.out.println("Second circle:");
        double x2 = scanner.nextDouble();
        double y2 = scanner.nextDouble();
        double r2 = scanner.nextDouble();

        CircleIntersection ci = new CircleIntersection(x1, y1, r1, x2, y2, r2);

        types result = ci.checkIntersection();


        switch (result) {
            case notInters:
                System.out.println("Do not intersect");
                break;
            case same:
                System.out.println("Circles are the same");
                break;
            case firstInside:
                System.out.println("The second circle is inside");
                break;
            case secondInside:
                System.out.println("The first circle is inside");
                break;
            case onePoint:
                System.out.println("Circles touch at one point");
                break;
            case twoPoints:
                System.out.println("Circles intersect at two points");
                break;
        }
    }
}
