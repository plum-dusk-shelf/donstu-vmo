package lab5;

import java.util.ArrayList;
import java.util.List;
import lab5.Bag;
import lab5.Pair;

class PairBag {
    private Bag bag;

    public PairBag(int capacity) {
        bag = new Bag(capacity);
    }

    public void addPair(Pair<?, ?> pair) {
        bag.add(pair);
    }

    public Pair<?, ?> getPair() {
        return (Pair<?, ?>) bag.get();
    }

    public int size() {
        return bag.size();
    }

    @Override
    public String toString() {
        return "PairBag{" +
                "bag=" + bag +
                '}';
    }

    public static void main(String[] args){
        PairBag pairBag = new PairBag(3);

        Pair<Integer, Integer> pair1 = new Pair<>(1, 2);
        Pair<Integer, String> pair2 = new Pair<>(3, "Hello");

        pairBag.addPair(pair1);
        pairBag.addPair(pair2);

        System.out.println(pairBag);

        Pair<?, ?> Pair1 = pairBag.getPair();
        Pair<?, ?> Pair2 = pairBag.getPair();

        System.out.println("Pair 1: " + Pair1);
        System.out.println("Pair 2: " + Pair2);
    }
}
