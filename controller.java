
public class controller {
    public static void main(String[] args) {
        // Declare two numbers
        int num1 = 40;
        int num2 = 40;

        // Perform addition
        int sum = math.add(num1, num2);

        // Print the result
        System.out.println("The sum of " + num1 + " and " + num2 + " is: " + sum);
    }

    public static int add(int num1, int num2) {
        return num1 + num2;
    }
}
