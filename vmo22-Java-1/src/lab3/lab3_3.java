public class lab3_3 {
    public static void main(String[] args) {
        int[][] array = {
            {-1, -2, -3, 4},
            {-5, 6, -7, 8},
            {9, -10, 11, -12}
        };
	for (int i = 0; i < array.length; i++) {
		for (int j = 0; j < array[i].length; j++) {
                	System.out.print(array[i][j] + " ");
        	}
        	System.out.println();
	}
        System.out.println();
	

        for (int i = 0; i < array.length; i++) {
		int[] line = array[i];
		for (int k = 0; k < line.length-1; k++){
			int minIndex = i;
			for (int m = i + 1; m < line.length; m++){
				if (line[m] < line[i]) minIndex = m;
			}
			if (minIndex != k){
				int buffer = line[i];
				line[i] = line[minIndex];
				line[minIndex] = buffer;
			}
		}
            }

	for (int i = 0; i < array.length; i++) {
		for (int j = 0; j < array[i].length; j++) {
                	System.out.print(array[i][j] + " ");
        	}
        	System.out.println();
	}
    }
}
