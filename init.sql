INSERT INTO cervezas_tipoingrediente (nombre_tipo) VALUES 
('Maltas'),
('Lúpulos'),
('Levaduras');
INSERT INTO cervezas_unidadmedida (nombre) VALUES ('kg');
-- Insertar Ingredientes: Maltas
INSERT INTO "cervezas_ingrediente" (nombre_ingrediente, tipo_id, unidad_id, stock) VALUES
('Pilsen', 1, 1, 0),
('Munich', 1, 1, 0),
('Abbey', 1, 1, 0),
('Cara Ruby', 1, 1, 0),
('Cara Blond', 1, 1, 0),
('Cara Clair', 1, 1, 0),
('Wheat Blanc', 1, 1, 0),
('Cebada Tostada', 1, 1, 0),
('Peated', 1, 1, 0),
('Pale Ale', 1, 1, 0),
('Cara Gold', 1, 1, 0),
('Chocolate', 1, 1, 0),
('Melano', 1, 1, 0),
('Black', 1, 1, 0),
('Special Belgium', 1, 1, 0),
('Crystal', 1, 1, 0);

-- Lúpulos
INSERT INTO "cervezas_ingrediente" (nombre_ingrediente, tipo_id, unidad_id, stock) VALUES
('Saaz', 2, 1, 0),
('Hallertau Mittelfruh', 2, 1, 0),
('Perle', 2, 1, 0),
('Polaris', 2, 1, 0),
('Cascada', 2, 1, 0),
('Mosaico', 2, 1, 0),
('Golding', 2, 1, 0),
('Fuggle', 2, 1, 0),
('Magnum', 2, 1, 0),
('Tettnang', 2, 1, 0),
('Nugget', 2, 1, 0);

-- Levaduras
INSERT INTO "cervezas_ingrediente" (nombre_ingrediente, tipo_id, unidad_id, stock) VALUES
('Safale S-33', 3, 1, 0),
('Safale BE-256', 3, 1, 0),
('Safale S-04', 3, 1, 0),
('Safale T58', 3, 1, 0);
INSERT INTO cervezas_receta (id, nombre_receta, descripcion, porcentaje_alcohol, contenido_neto, imagen) VALUES
(1, 'Abadía Ámbar', 'Notas de caramelo y dulces, fusión de malta Munich y Abbey. Leve amargo y característico dulzor.', 7.0, 350, NULL),
(2, 'Triple Blond', 'Rubia de alta graduación, aroma a malta, sutil sabor dulce, final amargo seco y placentero.', 9.0, 350, NULL),
(3, 'Cerveza Scotch', 'Estilo irlandés con semillas de roble, aromas a caramelo y granos tostados.', 6.5, 350, NULL),
(4, 'Belga Ahumada', 'Color marrón, aroma a pan y caramelo, sabor amaderado, excepcional.', 6.0, 350, NULL),
(5, 'Doppel Bock', 'Alta maltosidad, sabores acaramelados y tostados, cuerpo pleno, clásico alemán.', 10.2, 350, NULL),
(6, 'Stout Belga', 'Notas tostadas, retrogusto de chocolate y café, frutas oscuras y levaduras belgas.', 6.5, 350, NULL),
(7, 'Porter', 'Sabor a vainilla, malta tostada, chocolate, caramelo y tofe, con carácter floral.', 7.0, 350, NULL);
