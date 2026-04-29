# Overpass Queries de Referencia

## Endpoint
`https://overpass-api.de/api/interpreter`

## Query: Todos los edificios en bbox
```
[out:json][timeout:30];
(
  way["building"]({bbox});
  relation["building"]({bbox});
);
out body;
>;
out skel qt;
```

## Query: Edificios con niveles/altura
```
[out:json][timeout:30];
(
  way["building"]["building:levels"]({bbox});
  way["building"]["height"]({bbox});
);
out body;
>;
out skel qt;
```

## Query: Vías y calles
```
[out:json][timeout:30];
(
  way["highway"]({bbox});
);
out body;
>;
out skel qt;
```

## Query: Uso de suelo
```
[out:json][timeout:30];
(
  way["landuse"]({bbox});
  relation["landuse"]({bbox});
  way["leisure"]({bbox});
  way["natural"]({bbox});
);
out body;
>;
out skel qt;
```

## Query: POIs (amenities, shops, tourism)
```
[out:json][timeout:30];
(
  node["amenity"]({bbox});
  node["shop"]({bbox});
  node["tourism"]({bbox});
  node["sport"]({bbox});
);
out body;
```

## Query: Conteo rápido (para coverage profiler)
```
[out:json][timeout:15];
(
  way["building"]({bbox});
  node["amenity"]({bbox});
  way["highway"]({bbox});
);
out count;
```

## Query: Vegetación y áreas verdes
```
[out:json][timeout:30];
(
  way["natural"="tree_row"]({bbox});
  node["natural"="tree"]({bbox});
  way["landuse"="grass"]({bbox});
  way["leisure"="park"]({bbox});
  way["leisure"="garden"]({bbox});
);
out body;
>;
out skel qt;
```

## Query: Estacionamientos
```
[out:json][timeout:30];
(
  way["amenity"="parking"]({bbox});
  way["landuse"="parking"]({bbox});
);
out body;
>;
out skel qt;
```

## Formato bbox
`south,west,north,east` (latitudes y longitudes decimales)

Ejemplo para Estadio Kukulkán:
`20.9384,-89.5987,20.9438,-89.5933`
