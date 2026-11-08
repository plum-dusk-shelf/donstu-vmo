package lab4_2;

public class Complex {
    private final double real;
    private final double imag;

    // Конструкторы
    public Complex(double real, double imag) {
        this.real = real;
        this.imag = imag;
    }

    public Complex(double real) {
        this(real, 0);
    }

    // Геттеры
    public double getReal() {
        return real;
    }

    public double getImag() {
        return imag;
    }

    // Сложение
    public Complex add(Complex other) {
        return new Complex(this.real + other.real, this.imag + other.imag);
    }

    public Complex add(double other) {
        return new Complex(this.real + other, this.imag);
    }

    // Вычитание
    public Complex subtract(Complex other) {
        return new Complex(this.real - other.real, this.imag - other.imag);
    }

    public Complex subtract(double other) {
        return new Complex(this.real - other, this.imag);
    }

    // Умножение
    public Complex multiply(Complex other) {
        double realPart = this.real * other.real - this.imag * other.imag;
        double imagPart = this.real * other.imag + this.imag * other.real;
        return new Complex(realPart, imagPart);
    }

    public Complex multiply(double other) {
        return new Complex(this.real * other, this.imag * other);
    }

    // Деление
    public Complex divide(Complex other) {
        double denominator = other.real * other.real + other.imag * other.imag;
        double realPart = (this.real * other.real + this.imag * other.imag) / denominator;
        double imagPart = (this.imag * other.real - this.real * other.imag) / denominator;
        return new Complex(realPart, imagPart);
    }

    public Complex divide(double other) {
        return new Complex(this.real / other, this.imag / other);
    }

    // Комплексное сопряжение
    public Complex conjugate() {
        return new Complex(this.real, -this.imag);
    }

    public static boolean equals(Object obj1, Object obj2) {
        if (obj1 == obj2) return true;
        if (obj1 == null || obj2 == null || obj1.getClass() != obj2.getClass()) return false;
        Complex complex1 = (Complex) obj1;
        Complex complex2 = (Complex) obj2;
        return Double.compare(complex1.real, complex2.real) == 0 && Double.compare(complex1.imag, complex2.imag) == 0;
    }

    @Override
    public String toString() {
        if (imag >= 0) {
            return real + " + " + imag + "i";
        } else {
            return real + " - " + (-imag) + "i";
        }
    }

    public String toTrigonometricForm() {
        double magnitude = Math.sqrt(real * real + imag * imag);
        double angle = Math.atan2(imag, real);
        return magnitude + " * e^(i*" + angle + ")";
    }

    public static void main(String[] args) {
        Complex c1 = new Complex(3, 4);
        Complex c2 = new Complex(1, 2);

        System.out.println("c1 = " + c1.toString());
        System.out.println("c2 = " + c2.toString());

        boolean c1_c2_equals = Complex.equals(c1, c2);
        if (c1_c2_equals) System.out.println("c1 = c2");
        else System.out.println("c1 ≠ c2");

        System.out.println("c1 + c2 = " + c1.add(c2));
        System.out.println("c1 - c2 = " + c1.subtract(c2));
        System.out.println("c1 * c2 = " + c1.multiply(c2));
        System.out.println("c1 / c2 = " + c1.divide(c2));
        System.out.println("conjugate of c1: " + c1.conjugate());
        System.out.println("c1 in trigonometric form: " + c1.toTrigonometricForm());
    }
}
