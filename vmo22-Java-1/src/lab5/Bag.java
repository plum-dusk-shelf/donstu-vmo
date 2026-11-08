package lab5;

public final class Bag {
    private final Object[] elements;
    private int size;

    public Bag(int capacity) {
        this.elements = new Object[capacity];
        this.size = 0;
    }

    public void add(Object element) {
        if (size == elements.length) {
            throw new IllegalStateException("Bag is full");
        }
        int index = (int)Math.round(Math.random() * size);
        if (index < size) {
            System.arraycopy(elements, index, elements, index + 1, size - index);
        }
        elements[index] = element;
        size++;
    }

    public Object remove() {
        if (size == 0) {
            throw new IllegalStateException("Bag is empty");
        }
        int index = (int)Math.round(Math.random() * (size - 1));
        Object element = elements[index];
        System.arraycopy(elements, index + 1, elements, index, size - index - 1);
        size--;
        return element;
    }

    public Object get() {
        if (size == 0) {
            throw new IllegalStateException("Bag is empty");
        }
        int index = (int)Math.round(Math.random() * (size - 1));
        return elements[index];
    }

    public int size() {
        return size;
    }

    public static void main(String[] args) {
        Bag bag = new Bag(5);

        bag.add("apple");
        bag.add("banana");
        bag.add("cherry");

        System.out.println("Size: " + bag.size());
        System.out.println("Get: " + bag.get());
        System.out.println("Size: " + bag.size());
        System.out.println("Remove: " + bag.remove());
        System.out.println("Size: " + bag.size());

        bag.remove();
        bag.remove();
    }
}
