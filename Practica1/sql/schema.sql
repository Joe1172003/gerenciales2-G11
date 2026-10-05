DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS genero;
DROP TABLE IF EXISTS metodo_pago;
DROP TABLE IF EXISTS navegador;

-- 0 = Masculino, 1 = Femenino
CREATE TABLE genero (
    id_genero INT PRIMARY KEY,          
    nombre    VARCHAR(20) NOT NULL
);

-- 0 = Efectivo, 1 = T. Credito, 2 = T. Debito
CREATE TABLE metodo_pago (
    id_metodo_pago INT PRIMARY KEY,     
    nombre         VARCHAR(30) NOT NULL
);

-- 0 = Tienda Fisica, 1 a 4 = Navegador 1 a 4
CREATE TABLE navegador (
    id_navegador INT PRIMARY KEY,       
    nombre       VARCHAR(30) NOT NULL
);


CREATE TABLE clientes (
    id_cliente  INT PRIMARY KEY,
    edad        INT NOT NULL,
    id_genero   INT NOT NULL REFERENCES genero(id_genero),
    venta_total NUMERIC(10,2) NOT NULL,   -- total histórico gastado por el cliente
    n_compras   INT NOT NULL              -- cuántas compras lleva en total
);


CREATE TABLE compras (
    id_compra      SERIAL PRIMARY KEY,    
    id_cliente     INT NOT NULL REFERENCES clientes(id_cliente),
    fecha_compra   DATE NOT NULL,
    monto_compra   NUMERIC(10,3) NOT NULL, 
    id_metodo_pago INT NOT NULL REFERENCES metodo_pago(id_metodo_pago),
    id_navegador   INT NOT NULL REFERENCES navegador(id_navegador),
    tiempo         INT NOT NULL,           -- segundos que duro la visita
    boletin        SMALLINT NOT NULL,      -- 1 = si esta suscrito, 0 = no
    vale           SMALLINT NOT NULL       -- 1 = uso vale, 0 = no
);
