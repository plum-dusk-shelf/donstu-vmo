package lab4.car;

public class CarTest {
    public static void main(String[] args) {
        Engine ToyotaEngie = new Engine(200, 1.5, 5, "Gasoline", 3);

        Car car = new Car("Toyota", Car.CarType.LIGHT, "Red", ToyotaEngie, 4);
        car.setRegistrationNumber("А123ВВ77RUS");
        System.out.println("Brand: " + car.getBrand());
        System.out.println("Type: " + car.getType());
        System.out.println("Color: " + car.getColor());
        System.out.println("Engine Power: " + car.getEnginePower());
        System.out.println("Number of Wheels: " + car.getNumberOfWheels());
        System.out.println("Registration Number: " + car.getRegistrationNumber());

        car.setColor("Blue");
        car.setEnginePower(300);
        System.out.println("Updated Color: " + car.getColor());
        System.out.println("Updated Engine Power: " + car.getEnginePower());
    }
}

