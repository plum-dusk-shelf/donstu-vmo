package lab5;

public class Pair<T, U> {
    private T first;
    private U second;

    public static void main(String[] args) {
        Pair<String, Integer> pair = new Pair<>("Hello", 123);
        System.out.println(pair.getFirst());
        System.out.println(pair.getSecond());

        pair.setFirst("World");
        System.out.println(pair.getFirst());

        Pair<Double, Double> pair2 = Pair.make_pair(3.14, 2.71);
        System.out.println(pair2.getFirst());
    }

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    public T getFirst() {
        return first;
    }

    public void setFirst(T first) {
        this.first = first;
    }

    public U getSecond() {
        return second;
    }

    public void setSecond(U second) {
        this.second = second;
    }

    public String toString(){
        return this.getFirst() + " " + this.getSecond();
    }

    public static <T, U> Pair<T, U> make_pair(T first, U second) {
        return new Pair<>(first, second);
    }
}
