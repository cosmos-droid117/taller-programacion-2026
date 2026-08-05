public class Marine extends Personaje {
    private int ataque;

    public Marine(String nombre, int vida, int defensa, int ataque) {
        super(nombre, vida, defensa);
        this.ataque = ataque;
    }

    public int getAtaque() {
        return ataque;
    }

    public void setAtaque(int ataque) {
        this.ataque = ataque;
    }      
}
