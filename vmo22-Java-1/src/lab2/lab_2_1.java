public class lab_2_1{
	public static void main(String [] args){
		Byte b_max = Byte.MAX_VALUE;
		Byte b_min = Byte.MIN_VALUE;

		Integer i_max = Integer.MAX_VALUE;
		Integer i_min = Integer.MIN_VALUE;

		Short s_min = Short.MIN_VALUE;
		Short s_max = Short.MAX_VALUE;

		Long l_min = Long.MIN_VALUE;
		Long l_max = Long.MAX_VALUE;

		Double d_min = Double.MIN_VALUE;
		Double d_max = Double.MAX_VALUE;

		Float f_min = Float.MIN_VALUE;
		Float f_max = Float.MAX_VALUE;

		System.out.println(b_min + " - " + b_max);
		System.out.println(i_min + " - " + i_max);
		System.out.println(s_min + " - " + s_max);
		System.out.println(l_min + " - " + l_max);
		System.out.println(d_min + " - " + d_max);
		System.out.println(f_min + " - " + f_max);
	}
}
