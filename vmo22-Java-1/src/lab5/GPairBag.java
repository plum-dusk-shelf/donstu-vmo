package lab5;

import lab5.Bag;
import lab5.Pair;
import lab5.PairBag;

class GPairBag<T1, T2> {
    private Bag bag;

    public GPairBag(int capacity) {
        bag = new Bag(capacity);
    }

    public void addPair(Pair<T1, T2> pair) {
        bag.add(pair);
    }

    public Pair<T1, T2> getPair() {
        return (Pair<T1, T2>) bag.get();
    }

    public int size() {
        return bag.size();
    }

    @Override
    public String toString() {
        return "GPairBag{" +
                "bag=" + bag +
                '}';
    }

    public static void main(String[] args) {
        GPairBag<Integer, String> pairBag = new GPairBag<>(3);

        Pair<Integer, String> pair1 = new Pair<>(1, "One");
        Pair<Integer, String> pair2 = new Pair<>(2, "Two");

        pairBag.addPair(pair1);
        pairBag.addPair(pair2);

        System.out.println(pairBag);

        Pair<Integer, String> retrievedPair1 = pairBag.getPair();
        Pair<Integer, String> retrievedPair2 = pairBag.getPair();

        System.out.println("Retrieved Pair 1: " + retrievedPair1);
        System.out.println("Retrieved Pair 2: " + retrievedPair2);
    }
}