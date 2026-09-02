import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Cuadricula c = new Cuadricula(0, 0);
        Scanner input = new Scanner(System.in);

        System.out.println(" Cuantas columnas desea colocar");
        int x = input.nextInt();
        input.nextLine();
        c.setX(x);

        System.out.println(" Cuantas filas desea colocar");
        int y = input.nextInt();
        input.nextLine();
        c.setY(y);

        int[][] cuadro = new int[x][y];
        System.out.println("Cuadricula");
        for (int i = 0; i < cuadro.length; i++) {
            for (int j = 0; j < cuadro[i].length; j++) {
                System.out.print(cuadro[i][j] + " ");
            }
            System.out.println();
        }

        do {
            System.out.println("¿Que circulo desea rellenar?");
            int coordenada_nuevaX = input.nextInt();
            input.nextLine();
            int coordenada_nuevaY = input.nextInt();
            input.nextLine();
        }while();
    }
}
