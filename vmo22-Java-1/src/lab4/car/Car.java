package lab4.car;

import java.util.regex.Pattern;
import java.util.Random;

public class Car {
    private String registrationNumber;
    private final String brand;
    private final CarType type;
    private String color;
    private Engine engine;
    private final int numberOfWheels;

    public enum CarType {
        LIGHT, HEAVY
    }

    public Car(String brand, CarType type, String color, Engine engine, int numberOfWheels) {
        this.brand = brand;
        this.type = type;
        this.color = color;
        this.engine = engine;
        this.numberOfWheels = numberOfWheels;
    }

    public void setRegistrationNumber(String registrationNumber) {
        if (isValidRegistrationNumber(registrationNumber)) {
            this.registrationNumber = registrationNumber;
        } else {
            System.out.println("Invalid registration number");
        }
    }

    public void setColor(String color) {
        this.color = color;
    }

    public void setEnginePower(double enginePower) {
        this.engine.setPower(enginePower);
    }

    public String getRegistrationNumber() {
        return registrationNumber;
    }

    public String getBrand() {
        return brand;
    }

    public CarType getType() {
        return type;
    }

    public String getColor() {
        return color;
    }

    public double getEnginePower() {
        return engine.getPower();
    }

    public int getNumberOfWheels() {
        return numberOfWheels;
    }

    private boolean isValidRegistrationNumber(String registrationNumber) {
        String pattern = "[АВЕКМНОРСТУХ]\\d{3}[АВЕКМНОРСТУХ]{2}\\d{2,3}RUS";
        return Pattern.matches(pattern, registrationNumber);
    }
}

class Engine {
    private final int serialNumber;
    private double power;
    private final double volume;
    private final double fuelConsumption;
    private final String fuelType;
    private final int numberOfCylinders;

    // Конструктор
    public Engine(double power, double volume, double fuelConsumption, String fuelType, int numberOfCylinders) {
        Random rand = new Random();
        this.serialNumber = rand.nextInt(1000);
        this.power = power;
        this.volume = volume;
        this.fuelConsumption = fuelConsumption;
        this.fuelType = fuelType;
        this.numberOfCylinders = numberOfCylinders;
    }

    public int getSerialNumber() {
        return serialNumber;
    }

    public void setPower(double power){
        this.power = power;
    }

    public double getPower() {
        return power;
    }

    public double getVolume() {
        return volume;
    }

    public double getFuelConsumption() {
        return fuelConsumption;
    }

    public String getFuelType() {
        return fuelType;
    }

    public int getNumberOfCylinders() {
        return numberOfCylinders;
    }

    @Override
    public String toString() {
        return "Engine{" +
                "serialNumber='" + serialNumber + '\'' +
                ", power=" + power +
                ", volume=" + volume +
                ", fuelConsumption=" + fuelConsumption +
                ", fuelType='" + fuelType + '\'' +
                ", numberOfCylinders=" + numberOfCylinders +
                '}';
    }
}


