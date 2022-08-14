package Tasks;

import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		
		Scanner sc = new Scanner(System.in);
		System.out.println("Given DataSet");
		System.out.println("Assignment 1");
		int option = -1;
		while(option != 4) {
			displayOptions();
			option = sc.nextInt();
	
			switch(option) {
		
				case 1:{
					System.out.println("Executing Task1");
					Task1Ver1.main(args);
					break;
				}
				case 2:{
					System.out.println("Executing Task2");
					Task2Ver1.main(args);
					break;
				}
				case 3:{
					System.out.println("Executing Task3");
					Task3Ver1.main(args);
					break;
				}
				case 0:{
					System.out.println("Terminating");
					return;
				}
				default:{
					System.out.println("Enter invalid Task");
				}
				
			}
		}
		
	}
	public static void displayOptions() {
		System.out.println("Enter the task to execute");
		System.out.println("Task 1 (1)");
		System.out.println("Task 2 (2)");
		System.out.println("Task 3 (3)");
		System.out.println("End (0)");
	}

}
