public class pointers_1 {
    private static byte[] staticVar = new byte[32];

    private byte[] dynamicVar1 = new byte[32];
    private byte[] dynamicVar2 = new byte[32];
    private byte[] dynamicVar3 = new byte[32];
    private byte[] dynamicVar4 = new byte[32];

    public void setStaticSegmentValue(int index, byte value) {
        staticVar[index] = value;
    }

    public byte getStaticSegmentValue(int index) {
        return staticVar[index];	
    }

    public void switchStaticSegmentValue(int index1, int index2) {
	byte buffer = staticVar[index1];
	staticVar[index1] = staticVar[index2];
	staticVar[index2] = buffer;
    }

    public void freePointer(int index){
	staticVar[index] = 0;
    }


    public void main(String[] args){
    	for(int i = 0; i < 32; i++) {
		staticVar[i] = (byte) i;
    	}
    	System.out.println(staticVar);
    }
}
