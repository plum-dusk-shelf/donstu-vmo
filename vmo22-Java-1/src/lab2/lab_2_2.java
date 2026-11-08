import java.util.Arrays;
import java.lang.Math;

public class lab_2_2{
	public static void main(String[] args){
		int[] base_arr = {1,2,3,4,5,6,7,8,9,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10};
		double res = 1;

		for(int i = 0; i < base_arr.length; i++){
			if(base_arr[i]<0) res = res * base_arr[i];
		}
		res = Math.pow(res, 1/20);
		
		System.out.println(res);
	}
}
