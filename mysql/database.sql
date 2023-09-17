
use trustpilot;

CREATE TABLE CATEGORIE
(
  Id_categorie integer NOT NULL,
  Nom_categorie varchar(100) NOT NULL,
  Date_insertion datetime,
  Date_derniere_modification datetime,
  PRIMARY KEY(Id_categorie)
);

CREATE TABLE SITE
(
  Id_site integer NOT NULL,
  Nom_site varchar(100) NOT NULL,
  Note integer,
  Nombre_note integer,
  Pourcentage_etoile1 integer,
  Pourcentage_etoile2 integer,
  Pourcentage_etoile3 integer,
  Pourcentage_etoile4 integer,
  Pourcentage_etoile5 integer,
  Date_insertion datetime,
  Date_derniere_modification datetime,
  Id_categorie integer,
  PRIMARY KEY (Id_site),
  CONSTRAINT FK_Categorie_Site FOREIGN KEY (Id_categorie) REFERENCES CATEGORIE(Id_categorie)
);

