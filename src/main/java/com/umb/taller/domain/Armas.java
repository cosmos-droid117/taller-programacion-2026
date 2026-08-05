public class Armas {
    private String nombre;
    private int daño;
    private int alcance;

    public Armas(String nombre, int daño, int alcance) {
        this.nombre = nombre;
        this.daño = daño;
        this.alcance = alcance;
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public int getDaño() {
        return daño;
    }

    public void setDaño(int daño) {
        this.daño = daño;
    }

    public int getAlcance() {
        return alcance;
    }

    public void setAlcance(int alcance) {
        this.alcance = alcance;
    }
}
