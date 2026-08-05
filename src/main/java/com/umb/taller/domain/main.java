public class main {
    public static void main(String[] args) {
        Armas arma1 = new Armas("Espada", 50, 5);
        Armas arma2 = new Armas("Arco", 30, 10);

        Marine marine1 = new Marine("Marine1", 100, 20, 15);
        Marine marine2 = new Marine("Marine2", 80, 25, 20);

        System.out.println("Arma 1: " + arma1.getNombre() + ", Danio: " + arma1.getDaño() + ", Alcance: " + arma1.getAlcance());
        System.out.println("Arma 2: " + arma2.getNombre() + ", Danio: " + arma2.getDaño() + ", Alcance: " + arma2.getAlcance());

        System.out.println("Marine 1: " + marine1.getNombre() + ", Vida: " + marine1.getVida() + ", Defensa: " + marine1.getDefensa() + ", Ataque: " + marine1.getAtaque());
        System.out.println("Marine 2: " + marine2.getNombre() + ", Vida: " + marine2.getVida() + ", Defensa: " + marine2.getDefensa() + ", Ataque: " + marine2.getAtaque());
    }
    
}
