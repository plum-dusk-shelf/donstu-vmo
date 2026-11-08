package lab5;

import java.util.ArrayList;
import lab5.*;


class GenericPairBag<T1, T2> {
    private ArrayList<Pair<T1, T2>> pairs;

    public GenericPairBag() {
        pairs = new ArrayList<>();
    }

    public void addPair(Pair<T1, T2> pair) {
        pairs.add(pair);
    }

    public Pair<T1, T2> getPair(int index) {
        return pairs.get(index);
    }

    public int size() {
        return pairs.size();
    }

    public void remove(int index){
        pairs.remove(index);
    }

    @Override
    public String toString() {
        return "GenericPairBag{" +
                "pairs=" + pairs +
                '}';
    }

    public static void main(String[] args) {
        GenericPairBag<Integer, String> pairBag = new GenericPairBag<>();

        Pair<Integer, String> pair1 = new Pair<>(1, "One");
        Pair<Integer, String> pair2 = new Pair<>(2, "Two");

        pairBag.addPair(pair1);
        pairBag.addPair(pair2);

        System.out.println(pairBag);

        Pair<Integer, String> retrievedPair1 = pairBag.getPair(0);
        Pair<Integer, String> retrievedPair2 = pairBag.getPair(1);


        System.out.println("Retrieved Pair 1: " + retrievedPair1);
        System.out.println("Retrieved Pair 2: " + retrievedPair2);
    }
}

