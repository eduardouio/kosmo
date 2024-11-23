Detalle de Sotokcs

# Muestra 1 
1hb Explorer 40/50 x 250 0,40/0,50
1qb Explorer 60/70 x 100 0,60/0,70
1qb Freedom 40 x 125 0,30
4hb Freedom 50 x 500 0,35 
3hb Freedom 60 x 400 0,45
1hb Freedom 70 x 300 0,50
1qb Akito 40 x 125 0,35
2qb Akito 50 x 100 0,45
1hb Brighton 50/60/70 x 350 0,40/0,45/0,50
1qb Candlelight 40/50 x 125 0,50/0,60
1qb Country Blues 40 x 125 0,40
1hb Deep Purple 50/60 x 400 0,35/0,40
1hb Deep Purple 60 x 400 0,40
3qb Escimo 50 x 125 0,45
7qb Escimo 60 x 125 0,55
1qb Gotcha 60 x 100 0,60
1qb Hermosa 50/70 x 100 0,50/0,70
1qb High Magic 60 x 125 0,50
1hb Lola 40 x 350 0,30
1hb Nena 40 x 450 0,30
1qb Nena 50/60 x 100 0,40/0,45
1qb Orange Crush 40 x 125 0,35
1qb Orange Crush 50 x 100 0,50
1qb Ocean Song 40 x 125 0,35
1hb Ocean Song 50/60 x 350 0,44/0,48
1hb Pink Floyd 60 x 300 0,60
1qb Priceless 40/50 x 100 0,25/0,35
1qb Priceless 50/60 x 100 0,35/0,40
1qb Quicksand 40 x 100 0,70
2qb Sahara 40 x 125 0,70
1qb Sahara 50 x 100 0,80
1qb Secret Garden 40/50/60 x 100 0,30/0,34/0,38
1hb Secret Garden 60 x 400 0,38
1qb Secret Garden 60 x 100 0,38
1qb Shinmer 50 x 125 0,40
2hb Sweet Escimo 50 x 300 0,35
1qb Sweet Unique 40/50 x 125 0,30/0,40
1qb Sweet Unique 50/60 x 100 0,40/0,45
1qb Tara 60 x 100 0,45
3hb Mix 40 0,30



## Ejemplo de interpretacion
1hb Explorer 40/50 x 250 0,40/0,50 se lee como:
<ul>
    <li><strong>1</strong> cantidad</li>
    <li><strong>HB</strong> tipo de Caja Existen dos tipo que se usan (QB y HB)</li>
    <li><strong>Explorer</strong> es la Variedad de la flor</li>
    <li><strong>40/50</strong> Es la medida de los tallos en la casa, una sola flor en la caja</li>
    <li><strong>250</strong> Es la cantidad de tallos totales que hay en la caja</li>
    <li><strong>0,40/0,50</strong> Es el precio de la caja, el primero es el precio de la caja de 40 y el segundo el precio de la caja de 50</li>
</ul>

-- Ejemplo de salida esperada por línea, si algun dato no se obtiene se debe asignar el cero los datos requeridos son Variedad Cantidad de Cajas y tipo de caja
```json
{
        "quantity_box": 1,
        "box_model": "HB",
        "tot_stem_flower": 250,
        "box_items": [
            {
                "variety": "SECRET GARDEN",
                "tot_stem_flower": 0,
                "length": 40,
                "stem_cost_price": 0.3
            },
            {
                "variety": "SECRET GARDEN",
                "tot_stem_flower": 0,
                "length": 50,
                "stem_cost_price": 0.34,
            },
            {
                "variety": "SECRET GARDEN",
                "tot_stem_flower": 0,
                "length": 60,
                "stem_cost_price": 0.38,
            }
        ]
    }

```

2hb Sweet Escimo 50 x 300 0,35
<ul>
    <li><strong>2</strong> cantidad</li>
    <li><strong>HB</strong> tipo de Caja Existen dos tipo que se usan (QB y HB)</li>
    <li><strong>Sweet</strong> Escimo es la Variedad de la flor</li>
    <li><strong>50</strong> Es la medida de los tallos en la casa, significa que hay dos medidas de tallos en la caja</li>
    <li><strong>300</strong> Es la cantidad de tallos totales que hay en la caja</li>
    <li><strong>0,35</strong> Es el precio de la caja</li>
</ul>
```json
{
        "quantity_box": 2,
        "box_model": "HB",
        "tot_stem_flower": 300,
        "box_items": [
            {
                "variety": "SWEET ESCIMO",
                "tot_stem_flower": 0,
                "length": 50,
                "stem_cost_price": 0.35
            }
        ]
    }
```

# Segundo ejemplo de stock
AMARETO 1QB40	$	0,18
AMOROSA 1HB50	$	0,24
AMOROSA 1HB6070	$	0,28 0,32
DEEP PURPLE 1HB5060	$	0,24 0,28
DYNAMIC 1HB5060	$	0,24 0,28
ENGAGEMENT 1QB50	$	0,24
ESPERANCE 1HB50	$	0,24
ESPERANCE 1HB60	$	0,45
EXPLORER 8HB40	$	0,22
EXPLORER 20HB50	$	0,35
EXPLORER 4HB60	$	0,40
EXPLORER 3HB70	$	0,45
EXPLORER 1HB7080	$	0,45 0,50
FREEDOM 1HB5060	$	0,24 0,28
FRUTTETO 2HB40	$	0,18
FRUTTETO 2HB50	$	0,24
FULL MONTY 2HB50	$	0,24
FULL MONTY 1QB60	$	0,28
GOLDFINCH 1HB40	$	0,18
GOTCHA 1QB4050	$	0,18 0,24
HERMOSA 1HB6070	$	0,35 0,40
HOT EXPLORER 1QB50	$	0,24
KAHALA 1HB40	$	0,25
KAHALA 1HB50	$	0,35
LOLA 1QB50	$	0,24
MANDALA 3HB50	$	0,24
MIA 1QB40	$	0,18
MIA 1QB5060	$	0,24 0,28
MONDIAL 10HB40	$	0,18
MONDIAL 12HB50	$	0,24
MONDIAL 1HB60	$	0,28
MONDIAL 1HB70	$	0,32
MOODY BLUES 1HB50	$	0,24
MOODY BLUES 1HB60	$	0,28
MOONSTONE 1HB40	$	0,18
MOONSTONE 1HB50	$	0,24
MOONSTONE 1HB5060	$	0,24 0,28
NENA 1HB50	$	0,24
NENA 1HB60	$	0,28
NENA 1HB70	$	0,32
NEWSFLASH 1HB4050	$	0,18 0,24
NOVIA 1HB40	$	0,18
OCEAN SONG 1HB40	$	0,18
OCEAN SONG 1QB50	$	0,24
PINK FLOYD 1QB40	$	0,18
PINK FLOYD 1QB50	$	0,24
PINK MONDIAL 4HB40	$	0,18
PINK MONDIAL 4HB50	$	0,24
PLAYA BLANCA 1HB40	$	0,18
PLAYA BLANCA 2HB50	$	0,24
PLAYA BLANCA 2HB60	$	0,28
POMPEI 1QB5060	$	0,24 0,28
PRIMAVERA 1HB40	$	0,18
VERSILIA 1HB50	$	0,24
QUICKSAND 1QB40	$	0,18
QUICKSAND 2HB50	$	0,24
QUICKSAND 1HB6070	$	0,28 0,32
SAGA 1HB4050	$	0,18 0,24
SALMA 1HB50	$	0,24
SHIMMER 1QB40	$	0,18
SHIMMER 1QB50	$	0,24
SILANTOI 1QB50	$	0,24
SOUL 1QB40	$	0,18
SOUL 1HB50	$	0,24
SUPER SUN 1QB40	$	0,18
SWEET MEMORY 1HB5060	$	0,24 0,28
SWEET UNIQUE 1HB5060	$	0,24 0,28
TIBET 2HB40	$	0,18
TIBET 1QB50	$	0,24
TIFFANY 1QB40	$	0,18
TOPAZ 1HB5060	$	0,24 0,28
VENDELA 1HB4050	$	0,18 0,24
MIX 10HB40	$	0,18
MIX 10HB50	$	0,24
MIX 2HB60	$	0,28

AMARETO 1QB40	$	0,18
<ul>
    <strong>1</strong> cantidad
    <strong>QB</strong> tipo de Caja Existen dos tipo que se usan (QB y HB)
    <strong>AMARETO</strong> es la Variedad de la flor
    <strong>40</strong> Es la medida de los tallos en la casa, significa que hay una sola medida en la caja
    <strong>0,18</strong>Es el precio de la caja
</ul>
```json
{
        "quantity_box": 1,
        "box_model": "HB",
        "tot_stem_flower": 0,
        "box_items": [
            {
                "variety": "AMARETO",
                "tot_stem_flower": 0,
                "length": 40,
                "stem_cost_price": 0.18
            }
        ]
    }
```

## Tercer Muestra
AMOROSA 1HB6070 0.28 0.30
BE SWEET 1QB5060 0.40 0.50
BLUSH 1HB40 0.18 
BLUSH 1QB50 0.25
BRIGHTON 1HB40 0.18
CABARET 1QB40 0.18
CANDLELIGHT 1QB50 0.50
COOL WATER 1HB40 0.18
COOL WATER 1HB50  0.22
COTTON XPRESSION 1HB5060 0.50 0.60
DEEP PURPLE 1HB50 0.22
DEEP PURPLE 1HB60 0.26
DYNAMIC 1QB5060 0.30 0.035
EXPLORER 4HB40 0.25
EXPLORER 10HB50 0.35
FULL MONTY 2HB50 0.40
GOLDFINCH 1HB40 0.18
GOTCHA 1QB40 0.40
HIGH & BOOMING 1HB40 0.18
IGUANA 1HB40 0.18
KAHALA 1QB4050 0.25 0.38
LOLA 1QB4050 0.28 0.38
LORRAINE 1HB5060 0.28 0.32
MIA 1QB5060 0.28 0.32
MOMENTUM 1HB40 0.18
MONDIAL 5HB50 0.30
MOODY BLUES 1HB40 0.18
MOODY BLUES 1HB50 0.24
MOONSTONE 1HB5060 0.28 0.32
NENA 1HB5060 0.28 0.32
NEWSFLASH 1QB4050 0.24 0.35
NINA 1HB40 0.18
ORANGE BOWL 1QB40 0.22
PRIMAVERA 1HB40 0.18
SALMA 1QB5060 0.30 0.35
SHIMMER 1QB40 0.18
SILANTOI 1QB40 0.18
SOUL 1QB5060 0.28 0.32
STARDUST 1HB40 0.18
SWEETNESS 1HB4050 0.18 0.26
TOPAZ 1HB5060 0.26 0.30
TROTTOLA 1QB4050 0.22 0.35
VENDELA 1QB50 0.28
MIX 10HB40 0.18
MIX 10HB50 0.28
MIX  4HB60 0.32
******
RUSCUS  2HB40
RUSCUS  4HB50
RUSCUS  1HB5060

TOPAZ 1HB5060 0.26 0.30
<ul>
    <strong>1</strong> cantidad
    <strong>HB</strong> tipo de Caja Existen dos tipo que se usan (QB y HB)
    <strong>TOPAZ</strong> es la Variedad de la flor
    <strong>50/60</strong> Es la medida de los tallos en la casa, significa que hay dos medidas en la caja
    <strong>0.26/0.30</strong>Es el precio de la caja
</ul

```json

```

