import java.util.HashMap;

public class pointers_1 {
    private static byte[] staticVar = new byte[32];
    private static Byte[] dynamicVar1 = new Byte[32];
    private static Byte[] dynamicVar2 = new Byte[32];
    private static Byte[] dynamicVar3 = new Byte[32];
    private static Byte[] dynamicVar4 = new Byte[32];

    public static void setValue(int index, byte value) {
        staticVar[index] = value;
    }

    public static byte getValue(int index) {
        return staticVar[index];	
    }

    public static void switchValues(int index1, int index2) {
	byte buffer = staticVar[index1];
	staticVar[index1] = staticVar[index2];
	staticVar[index2] = buffer;
    }

    public static void freePointer(int index){
	staticVar[index] = 0;
    }

    public static void main(String[] args){
        HashMap<Integer, String> map = new HashMap<>();

    	int h = staticVar.hashCode();
    	System.out.println(h);
	System.out.println(System.identityHashCode(staticVar));
    	for(int i = 0; i < 32; i++) {
		staticVar[i] = (byte) i;
    	}
	
	byte B = 6;
	System.out.print(staticVar.toHexString());
	setValue(3, B);
	/* System.out.println(getValue(3)); */
	switchValues(3, 6);
	freePointer(3);
    }
}
