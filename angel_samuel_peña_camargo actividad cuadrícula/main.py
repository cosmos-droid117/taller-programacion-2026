# Programa para crear una cuadrícula de "○"
print("==============================================================================================================")
n = int(input("Ingrese la cantidad de columnas de la cuadrícula (mínimo 8): "))
m = int(input("Ingrese la cantidad de filas de la cuadrícula (mínimo 8): "))
print("==============================================================================================================")


# Validar que la cuadrícula sea mínimo 8x8
if n < 8 or m < 8:
    while n < 8 or m < 8:
        print("ERROR: La cuadrícula debe ser mínimo de 8x8.")
        print("==============================================================================================================")
        n = int(input("Ingrese la cantidad de columnas de la cuadrícula (mínimo 8): "))
        m = int(input("Ingrese la cantidad de filas de la cuadrícula (mínimo 8): "))
        print("==============================================================================================================")


# Crear matriz
matrix = []
for i in range(m):
    fila = []
    for j in range(n):
        fila.append("○")
    matrix.append(fila)


# Mostrar matriz inicial
for i in range(m):
    for j in range(n):
        print(matrix[i][j], end=" ")
    print()

# Menú
while True:
    print("\n1. Marcar puntos")
    print("2. Reiniciar Matriz")
    print("3. Salir")
    opcion = int(input("Seleccione una opción: "))
    
    if opcion == 1:
        print("==============================================================================================================")
        punto = int(input("Ingrese la cantidad de puntos a marcar: "))
        print("==============================================================================================================")
        lista_puntos = []
        # Pedir coordenadas
        for i in range(punto):
            n_user = int(input(f"Ingrese la coordenada X para marcar el punto {i+1}: "))
            m_user = int(input(f"Ingrese la coordenada Y para marcar el punto {i+1}: "))
            if 1 <= n_user <= n and 1 <= m_user <= m:
                lista_puntos.append((n_user, m_user))
            else:
                print(f"ERROR: Coordenada ({n_user}, {m_user}) fuera de los límites.")
            print("===============================================================================================================")
        # Marcar los puntos
        for punto in lista_puntos:
            n_user, m_user = punto
            # Validar coordenadas
            if n_user >= 1 and n_user <= n and m_user >= 1 and m_user <= m:
                matrix[m_user - 1][n_user - 1] = "●"
            else:
                print(f"ERROR: Coordenada {punto} fuera de los límites de la cuadrícula.")
        # Mostrar matriz
        print("\nCuadrícula:")
        for i in range(m):
            for j in range(n):
                print(matrix[i][j], end=" ")
            print()
        # Mostrar coordenadas
        print("\nCoordenadas ingresadas:", lista_puntos)
        print("==============================================================================================================")
        
    elif opcion == 2:
        # Reiniciar matriz
        matrix = []
        for i in range(m):
            fila = []
            for j in range(n):
                fila.append("○")
            matrix.append(fila)
        print()
        print("Matriz reiniciada.")
        
        for i in range(m):
            for j in range(n):
                print(matrix[i][j], end=" ")
            print()
        
        lista_puntos = []
        print("==============================================================================================================")

    elif opcion == 3:
        print()
        print("Programa finalizado.")
        break
    else:
        print()
        print("Opción inválida.")
