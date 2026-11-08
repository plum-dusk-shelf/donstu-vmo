public class lab3_2 {
    public static void main(String[] args) {
        int[][] array = {
            {-1, -2, -3, 4},
            {-5, 6, -7, 8},
            {9, -10, 11, -12}
        };
	
	int maxNegative = Integer.MIN_VALUE;

        for (int i = 0; i < array.length; i++) {
            for (int j = 0; j < array[i].length; j++) {
                if (array[i][j] < 0 && array[i][j] > maxNegative) {
                    maxNegative = array[i][j];
                }
            }
        }

        System.out.println("Maximum negative: " + maxNegative);
    }
}
